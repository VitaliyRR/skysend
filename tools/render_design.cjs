// Render code-native design boards. Original image pixels remain unchanged.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require(process.env.SKYSEND_SHARP_MODULE || 'sharp');
const root = path.resolve(__dirname, '..');
(async () => {
  for (const name of ['home-desktop', 'home-mobile', 'xml-detail-desktop']) {
    await sharp(path.join(root, 'design', `${name}.svg`))
      .flatten({background: '#ffffff'})
      .png()
      .toFile(path.join(root, 'design', `${name}.png`));
    console.log(`Rendered ${name}.png`);
  }
})();
