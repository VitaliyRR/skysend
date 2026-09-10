const fs=require('fs'),path=require('path');
const sharp=require(process.env.SKYSEND_SHARP_MODULE || 'sharp');
(async()=>{const entries=[...fs.readdirSync('assets/diagrams').map(n=>'assets/diagrams/'+n),'assets/brand/skysend-logo.svg'];for(const p of entries){await sharp(p).flatten({background:'#ffffff'}).png().toFile('assets/contact-sheets/'+path.basename(p,'.svg')+'-preview.png')}console.log('Rendered',entries.length,'SVGs');})();
