const { NotionAPI } = require('notion-client')
async function main() {
  const api = new NotionAPI({ apiBaseUrl: 'https://www.notion.so/api/v3' })
  const data = await api.getPage('ca1a6948-a53f-4562-a47c-e83a9412b4b7')
  const blocks = data?.block || {}
  const self = blocks['ca1a6948-a53f-4562-a47c-e83a9412b4b7']?.value?.value || blocks['ca1a6948-a53f-4562-a47c-e83a9412b4b7']?.value
  console.log('LOFT page format:', JSON.stringify(self?.format || {}, null, 1).slice(0, 500))
  console.log('LOFT properties title:', JSON.stringify(self?.properties?.title || self?.properties, null, 1).slice(0, 300))
  // 看子页面 Me 的 icon
  const content = self?.content || []
  for (const cid of content) {
    const b = blocks[cid]?.value?.value || blocks[cid]?.value
    if (b?.type === 'column_list') {
      for (const colId of (b.content || [])) {
        const col = blocks[colId]?.value?.value || blocks[colId]?.value
        for (const gid of (col?.content || [])) {
          const gb = blocks[gid]?.value?.value || blocks[gid]?.value
          if (gb?.type === 'child_page') {
            console.log('child_page:', gb?.properties?.title?.[0]?.[0], '| icon:', JSON.stringify(gb?.format?.page_icon || gb?.format?.icon || null))
          }
        }
      }
    }
  }
}
main().catch(e => console.error('FAIL', e.message))
