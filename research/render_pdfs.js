// Render the two review PDFs from their pdfmake specs.
// Run:  python research/build_pdfs.py    (writes tmp/*.pdf.json)
// then: node research/render_pdfs.js     (writes outputs/*.pdf)
const fs = require('fs');
const path = require('path');

const TMP = path.join(__dirname, '..', 'tmp');
// pdfmake 0.3's node entry exports a ready instance, not a class.
const dp = require(path.join(TMP, 'node_modules', 'pdfmake'));
dp.setLocalAccessPolicy(() => true);

const fonts = {
  Roboto: {
    normal: path.join(TMP, 'fonts', 'Roboto-Regular.ttf'),
    bold: path.join(TMP, 'fonts', 'Roboto-Medium.ttf'),
    italics: path.join(TMP, 'fonts', 'Roboto-Italic.ttf'),
    bolditalics: path.join(TMP, 'fonts', 'Roboto-MediumItalic.ttf')
  }
};
dp.setFonts(fonts);

(async () => {
  for (const name of ['baseline-register', 'gdpr-controls-proposal']) {
    const spec = JSON.parse(
      fs.readFileSync(path.join(TMP, name + '.pdf.json'), 'utf8'));
    const doc = await dp.createPdf(spec);
    const out = path.join(__dirname, '..', 'outputs', name + '.pdf');
    await doc.write(out);
    console.log('wrote', out, fs.statSync(out).size, 'bytes');
  }
})();
