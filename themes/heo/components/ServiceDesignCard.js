import SmartLink from '@/components/SmartLink'

/**
 * 首页右侧栏「服务设计」板块入口
 * 垂直紧凑卡片，适配 w-72 侧栏宽度
 */
export default function ServiceDesignCard() {
  return (
    <SmartLink
      href='/service-design'
      className='group relative block overflow-hidden rounded-xl border dark:border-gray-700 bg-[var(--heo-color-card)] dark:bg-[var(--heo-color-card-dark)] transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5'>
      {/* 顶部渐变主色条 */}
      <div className='h-1.5 w-full bg-gradient-to-r from-[var(--heo-color-primary)] to-[var(--heo-color-accent)]' />

      <div className='p-4'>
        <div className='flex items-center gap-3'>
          {/* 图标 */}
          <div className='flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--heo-color-primary)] text-[var(--heo-color-primary-text)] shadow-md transition-transform duration-300 group-hover:scale-110'>
            <svg
              className='h-5 w-5'
              viewBox='0 0 24 24'
              fill='none'
              stroke='currentColor'
              strokeWidth='2'
              strokeLinecap='round'
              strokeLinejoin='round'>
              <path d='M12 2L2 7l10 5 10-5-10-5z' />
              <path d='M2 17l10 5 10-5' />
              <path d='M2 12l10 5 10-5' />
            </svg>
          </div>

          {/* 标题 */}
          <div className='min-w-0'>
            <div className='flex items-center gap-1.5'>
              <span className='text-base font-bold text-gray-900 dark:text-white'>
                服务设计
              </span>
              <span className='rounded bg-[var(--heo-color-card-muted)] px-1.5 py-0.5 text-[10px] text-gray-500 dark:text-gray-400'>
                知识体系
              </span>
            </div>
            <div className='mt-0.5 truncate text-xs text-gray-500 dark:text-gray-400'>
              从概念到实施 · 五张核心地图
            </div>
          </div>
        </div>

        {/* 底部按钮 */}
        <div className='mt-3 flex items-center justify-between rounded-lg bg-[var(--heo-color-card-muted)] px-3 py-1.5 transition-colors duration-300 group-hover:bg-[var(--heo-color-primary)] group-hover:text-[var(--heo-color-primary-text)]'>
          <span className='text-xs font-bold'>查看总纲</span>
          <svg
            className='h-3.5 w-3.5 transition-transform duration-300 group-hover:translate-x-0.5'
            viewBox='0 0 24 24'
            fill='none'
            stroke='currentColor'
            strokeWidth='2.5'
            strokeLinecap='round'
            strokeLinejoin='round'>
            <path d='M5 12h14' />
            <path d='M12 5l7 7-7 7' />
          </svg>
        </div>
      </div>
    </SmartLink>
  )
}
