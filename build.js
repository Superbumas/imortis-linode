const { readFileSync, writeFileSync } = require('fs');
const { compileTemplate, compileScript, parse } = require('@vue/compiler-sfc');

const filePath = 'static/components/ProfileTimeline.vue';
const fileContent = readFileSync(filePath, 'utf-8');

const { descriptor } = parse(fileContent);

const { code: templateCode } = compileTemplate({
  source: descriptor.template.content,
  filename: filePath,
  id: 'ProfileTimeline'  // Add the id option here
});

const { code: scriptCode } = compileScript(descriptor, {
  id: 'ProfileTimeline',
});

const outputCode = `
${scriptCode}
${templateCode}
`;

writeFileSync('static/components/ProfileTimeline.js', outputCode);