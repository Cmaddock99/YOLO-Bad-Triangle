const fs = require("fs/promises");
const path = require("path");
const { chromium } = require("./tmp/playwright_core/node_modules/playwright-core");

const CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const ROOT = "/Users/lurch/ml-labs/YOLO-Bad-Triangle/Homework";
const OUT_DIR = path.join(ROOT, "output", "playwright");

const layers = [
  {
    title: "Sponge Attack on Public NLP API",
    file: path.join(ROOT, "layers", "sponge_attack_layer.json"),
    out: path.join(OUT_DIR, "sponge_attack_render.png"),
  },
  {
    title: "Audio Adversarial Perturbation",
    file: path.join(ROOT, "layers", "audio_adversarial_perturbation_layer.json"),
    out: path.join(OUT_DIR, "audio_adversarial_perturbation_render.png"),
  },
  {
    title: "Hugging Face Repository Hijack",
    file: path.join(ROOT, "layers", "hugging_face_repository_hijack_layer.json"),
    out: path.join(OUT_DIR, "hugging_face_repository_hijack_render.png"),
  },
];

async function acceptAnyDialog(page, dialogMessages) {
  page.on("dialog", async (dialog) => {
    dialogMessages.push(dialog.message());
    await dialog.dismiss();
  });
}

async function openNavigator(page) {
  // The root route may auto-open saved/default tabs. Landing on a bad layer URL
  // reliably drops us onto the "Open Existing Layer" home view instead.
  await page.goto("https://mitre-atlas.github.io/atlas-navigator/#layerURL=http://127.0.0.1:8765/invalid.json", {
    waitUntil: "networkidle",
  });

  const openExistingLayer = page.getByRole("button", {
    name: /Open Existing Layer/,
  });

  await openExistingLayer.waitFor({ state: "visible", timeout: 15000 });
  return openExistingLayer;
}

async function uploadLayer(page, layer) {
  const openExistingLayer = await openNavigator(page);
  await openExistingLayer.click();

  const uploadButton = page.getByRole("button", { name: "Upload from local" });
  const [fileChooser] = await Promise.all([
    page.waitForEvent("filechooser"),
    uploadButton.click(),
  ]);

  await fileChooser.setFiles(layer.file);
  await page.getByText(layer.title).first().waitFor({ timeout: 15000 });
}

async function waitForRenderedDialog(dialog) {
  const deadline = Date.now() + 15000;

  while (Date.now() < deadline) {
    const text = ((await dialog.textContent()) || "")
      .replace(/\s+/g, " ")
      .trim();

    const loaded =
      text.length > 80 &&
      !/loading\.\.\./i.test(text) &&
      text.includes("about") &&
      text.includes("domain") &&
      text.includes("close");

    if (loaded) {
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, 250));
  }

  throw new Error("Timed out waiting for rendered ATLAS export dialog");
}

async function renderScreenshot(browser, layer) {
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1200 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const dialogMessages = [];
  await acceptAnyDialog(page, dialogMessages);

  try {
    await uploadLayer(page, layer);
    await page.getByText("camera_alt").click();

    const dialog = page.getByRole("dialog");
    await dialog.waitFor({ state: "visible", timeout: 15000 });
    await waitForRenderedDialog(dialog);
    await dialog.screenshot({
      path: layer.out,
      type: "png",
    });
  } finally {
    await context.close();
  }

  const unexpectedDialogs = dialogMessages.filter(
    (message) => !message.includes("invalid.json"),
  );

  if (unexpectedDialogs.length > 0) {
    throw new Error(
      `Navigator displayed dialogs while rendering ${layer.title}: ${unexpectedDialogs.join(
        " | ",
      )}`,
    );
  }
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });

  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROME_PATH,
  });

  try {
    for (const layer of layers) {
      await renderScreenshot(browser, layer);
      console.log(`saved ${path.basename(layer.out)}`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
