// Screenshot a story flow page in light, dark, and light switched to dark
// after load, and report diagrams that failed to draw.
// Run from a directory where `playwright` is installed (the frontend checkout):
//   node <this file> <page.html> <out-dir>
import { createRequire } from 'node:module'
import { resolve } from 'node:path'

const { chromium } = createRequire(resolve(process.cwd()) + '/')('playwright')
const [file, outDir] = process.argv.slice(2)
if (!file || !outDir) {
  console.error('usage: node shoot.mjs <page.html> <out-dir>')
  process.exit(2)
}

const browser = await chromium.launch()
let failed = false
for (const [scheme, switchTo] of [['light'], ['dark'], ['light', 'dark']]) {
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 }, colorScheme: scheme })
  const errors = []
  page.on('pageerror', (e) => errors.push(String(e)))
  await page.goto('file://' + resolve(file))
  const panels = await page.locator('.panel').count()
  await page
    .waitForFunction((n) => document.querySelectorAll('.drawn svg').length === n * 2, panels, { timeout: 90000 })
    .catch(() => {})
  if (switchTo) await page.evaluate((t) => document.documentElement.setAttribute('data-theme', t), switchTo)
  const name = switchTo ? `${scheme}-to-${switchTo}` : scheme
  const notDrawn = await page.evaluate(() =>
    [...document.querySelectorAll('.drawn')].map((d) => d.textContent).filter((t) => t.startsWith('この図を描けませんでした')),
  )
  for (let i = 0; i < panels; i++) {
    await page.locator('.panel').nth(i).screenshot({ path: `${outDir}/${name}-diagram-${i + 1}.png` })
  }
  await page.screenshot({ path: `${outDir}/${name}-page.png`, fullPage: true })
  console.log(`${name}: ${panels} diagrams, ${notDrawn.length} not drawn, ${errors.length} page errors`)
  for (const t of [...notDrawn, ...errors]) console.log('  ' + t.slice(0, 300))
  if (notDrawn.length || errors.length) failed = true
  await page.close()
}
await browser.close()
process.exit(failed ? 1 : 0)
