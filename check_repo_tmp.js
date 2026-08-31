const fs = require('fs');
const os = require('os');
const path = require('path');
const cred = fs.readFileSync(path.join(os.homedir(), '.git-credentials'), 'utf8').trim();
const token = cred.split('@')[0].split(':').slice(2).join(':');

const PATTERNS = [
  ['2504', 'Windows用户名'],
  ['Users', '本机用户路径'],
  ['workbuddy', '本机工作区路径'],
  ['127.0.0.1', '本机代理'],
  ['git-credentials', '凭证文件引用'],
  ['SESSDATA|bili_jct|PSID|LOGIN_INFO', 'Cookie值特征'],
  ['[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+', '邮箱'],
  ['1[3-9][0-9]{9}', '手机号'],
];

async function main() {
  const r = await fetch('https://api.github.com/repos/Simiely/video-split-flac/git/trees/main?recursive=1', {
    headers: { 'Authorization': 'Bearer ' + token, 'User-Agent': 'workbuddy' }
  });
  const tree = await r.json();
  const files = tree.tree.filter(x => x.type === 'blob');
  console.log('共', files.length, '个文件');
  let anyHit = false;
  for (const f of files) {
    const c = await fetch(f.url, { headers: { 'Authorization': 'Bearer ' + token, 'User-Agent': 'workbuddy' } });
    const data = await c.json();
    const content = Buffer.from(data.content, 'base64').toString('utf8');
    for (const [pat, desc] of PATTERNS) {
      const re = new RegExp(pat, 'i');
      const lines = content.split('\n').filter(l => re.test(l));
      if (lines.length) {
        anyHit = true;
        console.log('[' + desc + '] ' + f.path + ' (' + lines.length + '行):');
        lines.slice(0, 2).forEach(l => console.log('    ' + l.trim().slice(0, 110)));
      }
    }
  }
  console.log(anyHit ? '=== 发现残留，需清理 ===' : '=== 全部干净 ===');
}
main().catch(e => console.log('ERR:', e.message));
