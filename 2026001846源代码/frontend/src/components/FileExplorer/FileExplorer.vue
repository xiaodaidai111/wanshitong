<template>
  <view class="fe-root">
    <!-- 顶部工具栏 -->
    <view class="fe-toolbar">
      <view class="fe-search" :class="{ focused: searchFocused }">
        <text class="fe-search-icon">🔍</text>
        <input class="fe-search-input" v-model="searchText" placeholder="搜索文件、手册、案例..." @focus="searchFocused = true" @blur="searchFocused = false" @input="onSearch" />
        <text class="fe-search-clear" v-if="searchText" @click="searchText = ''; onSearch()">✕</text>
      </view>
      <view class="fe-actions">
        <view class="fe-action-btn" @click="showNewFolder = true"><text class="fe-action-icon">📁+</text></view>
      </view>
    </view>

    <!-- 面包屑路径 -->
    <view class="fe-breadcrumb" v-if="breadcrumbs.length > 1">
      <view v-for="(bc, i) in breadcrumbs" :key="i" class="fe-crumb" @click="navigateTo(bc.id)">
        <text class="fe-crumb-text" :class="{ active: i === breadcrumbs.length - 1 }">{{ bc.name }}</text>
        <text class="fe-crumb-sep" v-if="i < breadcrumbs.length - 1">/</text>
      </view>
    </view>

    <!-- 快捷分类 -->
    <view class="fe-cats" v-if="!currentFolder && quickCategories.length">
      <scroll-view scroll-x class="fe-cats-scroll">
        <view class="fe-cats-inner">
          <view v-for="(cat, i) in quickCategories" :key="i" class="fe-cat-chip" :class="{ active: activeQuickCat === cat.key }" @click="toggleQuickCat(cat.key)">
            <text class="fe-cat-label">{{ cat.label }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 排序/筛选/批量 工具条 -->
    <view class="fe-subbar">
      <view class="fe-subbar-left">
        <view class="fe-sort-btn" @click="cycleSort">
          <text class="fe-sort-icon">{{ sortIcon }}</text>
          <text class="fe-sort-label">{{ sortLabel }}</text>
        </view>
        <view class="fe-filter-btn" :class="{ active: typeFilter }" @click="cycleTypeFilter">
          <text class="fe-filter-icon">🔽</text>
          <text class="fe-filter-label">{{ typeFilter || '全部类型' }}</text>
        </view>
      </view>
      <view class="fe-subbar-right">
        <view class="fe-batch-btn" :class="{ active: batchMode }" @click="batchMode = !batchMode; selectedIds = []">
          <text class="fe-batch-icon">{{ batchMode ? '✕' : '☑' }}</text>
          <text class="fe-batch-label">{{ batchMode ? '取消' : '批量' }}</text>
        </view>
      </view>
    </view>

    <!-- 批量操作栏 -->
    <view class="fe-batch-bar" v-if="batchMode && selectedIds.length > 0">
      <text class="fe-batch-count">已选 {{ selectedIds.length }} 项</text>
      <view class="fe-batch-actions">
        <view class="fe-ba-btn" @click="batchAddToKB"><text>加入知识库</text></view>
        <view class="fe-ba-btn" @click="batchMove"><text>移动</text></view>
        <view class="fe-ba-btn danger" @click="batchDelete"><text>删除</text></view>
      </view>
    </view>

    <!-- 最近文件 (仅根目录) -->
    <view class="fe-recent" v-if="!currentFolder && !searchText && !activeQuickCat">
      <text class="fe-section-title">最近文件</text>
      <scroll-view scroll-x class="fe-recent-scroll">
        <view class="fe-recent-inner">
          <view v-for="f in recentFiles" :key="f.id" class="fe-recent-card" @click="openFile(f)">
            <text class="fe-recent-name">{{ f.name }}</text>
            <text class="fe-recent-time">{{ formatTime(f.updateTime) }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 文件列表 -->
    <scroll-view scroll-y class="fe-list-scroll" @scrolltolower="loadMore">
      <!-- 文件列表 -->
      <view class="fe-list">
        <view v-for="f in displayFiles" :key="f.id" class="fe-list-item" :class="{ selected: selectedIds.includes(f.id) }" @click="onItemClick(f)" @longpress="onItemLongPress(f)">
          <view class="fe-checkbox" v-if="batchMode" @click.stop="toggleSelect(f.id)">
            <text class="fe-check-icon">{{ selectedIds.includes(f.id) ? '☑' : '☐' }}</text>
          </view>
          <view class="fe-item-info">
            <view class="fe-item-name-row">
              <text class="fe-item-name">{{ f.name }}</text>
              <text class="fe-star" v-if="f.starred" @click.stop="f.starred = !f.starred">⭐</text>
            </view>
            <view class="fe-item-meta-row">
              <text class="fe-item-meta">{{ f.uploader }}</text>
              <text class="fe-item-meta" v-if="f.type !== 'folder'">{{ formatSize(f.size) }}</text>
              <text class="fe-item-meta">{{ formatTime(f.updateTime) }}</text>
            </view>
            <view class="fe-item-tags" v-if="f.tags && f.tags.length">
              <text class="fe-item-tag" v-for="(t, ti) in f.tags.slice(0, 3)" :key="ti">{{ t }}</text>
              <view class="fe-parse-badge" v-if="f.type !== 'folder'" :class="'parse-' + f.parseStatus">
                {{ parseLabel(f.parseStatus) }}
              </view>
            </view>
          </view>
          <view class="fe-item-more" @click.stop="showFileMenu(f)">
            <text class="fe-more-icon">⋯</text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="fe-empty" v-if="displayFiles.length === 0 && !loading">
        <text class="fe-empty-icon">{{ searchText ? '🔍' : '📂' }}</text>
        <text class="fe-empty-text">{{ searchText ? '未找到匹配的文件' : '此文件夹为空' }}</text>
      </view>

      <!-- 加载状态 -->
      <view class="fe-loading" v-if="loading">
        <view class="fe-loading-spinner"></view>
        <text class="fe-loading-text">加载中...</text>
      </view>
    </scroll-view>

    <!-- 文件详情弹窗 -->
    <view class="fe-detail-mask" v-if="detailFile" @click="closeDetail">
      <view class="fe-detail-panel" @click.stop="">
        <view class="fe-detail-header">
          <text class="fe-detail-title">{{ readerMode ? '阅读文件' : '文件详情' }}</text>
          <text class="fe-detail-close" @click="readerMode = false; detailFile = null">✕</text>
        </view>
        <!-- 阅读模式 -->
        <scroll-view scroll-y class="fe-reader-body" v-if="readerMode">
          <view class="fe-reader-meta">
            <text class="fe-reader-source">📖 {{ detailFile.uploader }} · {{ detailFile.category }}</text>
            <view class="fe-reader-tags" v-if="detailFile.tags && detailFile.tags.length">
              <text class="fe-reader-tag" v-for="(t, i) in detailFile.tags" :key="i">{{ t }}</text>
            </view>
          </view>
          <text class="fe-reader-content">{{ detailFile.readContent || '暂无预览内容。此文件需要下载后使用对应应用程序打开。' }}</text>
        </scroll-view>
        <!-- 详情模式 -->
        <scroll-view scroll-y class="fe-detail-body" v-if="!readerMode">
          <!-- 预览区 -->
          <view class="fe-preview-area">
            <view class="fe-preview-icon-wrap" :style="{ background: getTypeBg(detailFile.type) }">
              <text class="fe-preview-icon">{{ getTypeIcon(detailFile.type) }}</text>
            </view>
            <image v-if="detailFile.type === 'image'" :src="detailFile.thumbnail" mode="aspectFit" class="fe-preview-img" />
          </view>
          <!-- 信息列表 -->
          <view class="fe-info-list">
            <view class="fe-info-row"><text class="fe-info-label">文件名</text><text class="fe-info-value">{{ detailFile.name }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">类型</text><text class="fe-info-value">{{ detailFile.ext?.toUpperCase() || detailFile.type }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">大小</text><text class="fe-info-value">{{ formatSize(detailFile.size) }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">分类</text><text class="fe-info-value">{{ detailFile.category }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">上传人</text><text class="fe-info-value">{{ detailFile.uploader }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">上传时间</text><text class="fe-info-value">{{ detailFile.uploadTime }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">更新时间</text><text class="fe-info-value">{{ detailFile.updateTime }}</text></view>
            <view class="fe-info-row" v-if="detailFile.equipmentName"><text class="fe-info-label">关联设备</text><text class="fe-info-value link">{{ detailFile.equipmentName }}</text></view>
            <view class="fe-info-row" v-if="detailFile.taskTitle"><text class="fe-info-label">关联任务</text><text class="fe-info-value link">{{ detailFile.taskTitle }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">知识库</text><text class="fe-info-value">{{ detailFile.inKnowledgeBase ? '✅ 已加入' : '未加入' }}</text></view>
            <view class="fe-info-row"><text class="fe-info-label">AI解析</text><text class="fe-info-value" :class="'parse-text-' + detailFile.parseStatus">{{ parseLabel(detailFile.parseStatus) }}</text></view>
          </view>
          <!-- 操作按钮 -->
          <view class="fe-detail-actions">
            <view class="fe-da-btn primary" v-if="detailFile.type !== 'folder'" @click="readerMode = true"><text>📖 阅读文件</text></view>
            <view class="fe-da-btn" @click="toggleStar(detailFile)"><text>{{ detailFile.starred ? '⭐ 取消收藏' : '☆ 加入收藏' }}</text></view>
            <view class="fe-da-btn" @click="renameFile(detailFile)"><text>✏️ 重命名</text></view>
            <view class="fe-da-btn" v-if="!detailFile.inKnowledgeBase" @click="addToKB(detailFile)"><text>📚 加入知识库</text></view>
            <view class="fe-da-btn" @click="moveFile(detailFile)"><text>📦 移动</text></view>
            <view class="fe-da-btn danger" @click="deleteFile(detailFile)"><text>🗑️ 删除</text></view>
          </view>
        </scroll-view>
        <!-- 底部关闭按钮（固定在面板底部） -->
        <view class="fe-detail-close-bar" @click="closeDetail"><text class="fe-detail-close-bar-text">✕ 关闭</text></view>
      </view>
    </view>

    <!-- 新建文件夹弹窗 -->
    <view class="fe-modal-mask" v-if="showNewFolder" @click="showNewFolder = false">
      <view class="fe-modal-box" @click.stop>
        <text class="fe-modal-title">新建文件夹</text>
        <input class="fe-modal-input" v-model="newFolderName" placeholder="文件夹名称" />
        <view class="fe-modal-btns">
          <view class="fe-mbtn cancel" @click="showNewFolder = false"><text>取消</text></view>
          <view class="fe-mbtn confirm" @click="createFolder"><text>创建</text></view>
        </view>
      </view>
    </view>

    <!-- 文件操作菜单 -->
    <view class="fe-menu-mask" v-if="menuFile" @click="menuFile = null">
      <view class="fe-menu-panel" @click.stop>
        <view class="fe-menu-item" @click="detailFile = menuFile; menuFile = null"><text>📋 查看详情</text></view>
        <view class="fe-menu-item" @click="renameFile(menuFile)"><text>✏️ 重命名</text></view>
        <view class="fe-menu-item" @click="toggleStar(menuFile)"><text>{{ menuFile.starred ? '⭐ 取消收藏' : '☆ 收藏' }}</text></view>
        <view class="fe-menu-item" v-if="!menuFile.inKnowledgeBase && menuFile.type !== 'folder'" @click="addToKB(menuFile)"><text>📚 加入知识库</text></view>
        <view class="fe-menu-item" @click="moveFile(menuFile)"><text>📦 移动到...</text></view>
        <view class="fe-menu-item danger" @click="deleteFile(menuFile)"><text>🗑️ 删除</text></view>
        <view class="fe-menu-cancel" @click="menuFile = null"><text>取消</text></view>
      </view>
    </view>

  </view>
</template>

<script>
// ===== 数据结构定义 =====
// FileItem: { id, name, type, size, parentId, path, category, tags, uploader, uploadTime, updateTime, equipmentId, equipmentName, taskId, taskTitle, inKnowledgeBase, parseStatus, starred, thumbnail, ext }
// UploadTask: { file, category, tags, equipmentId, equipmentName, taskTitle, addToKB, progress, status, error }
// FileParseStatus: 'none' | 'pending' | 'parsing' | 'done' | 'failed'

let _fileId = 100
function makeFile(overrides) {
  return {
    id: 'f' + (++_fileId),
    name: '未命名文件',
    type: 'document',
    size: 0,
    parentId: null,
    category: '附件',
    tags: [],
    uploader: '张工',
    uploadTime: '2026-06-10 09:00',
    updateTime: '2026-06-10 09:00',
    equipmentId: null,
    equipmentName: '',
    taskId: null,
    taskTitle: '',
    inKnowledgeBase: false,
    parseStatus: 'none',
    starred: false,
    thumbnail: '',
    ext: '',
    ...overrides,
  }
}

const MOCK_FILES = [
  // 根目录文件夹
  makeFile({ id: 'f1', name: '设备手册', type: 'folder', category: '手册', uploader: '系统', updateTime: '2026-06-10', size: 0 }),
  makeFile({ id: 'f2', name: '故障案例', type: 'folder', category: '案例', uploader: '系统', updateTime: '2026-06-09', size: 0 }),
  makeFile({ id: 'f3', name: '标准流程', type: 'folder', category: '流程', uploader: '系统', updateTime: '2026-06-08', size: 0 }),
  makeFile({ id: 'f4', name: '检修报告', type: 'folder', category: '报告', uploader: '系统', updateTime: '2026-06-07', size: 0 }),
  makeFile({ id: 'f5', name: '现场附件', type: 'folder', category: '附件', uploader: '系统', updateTime: '2026-06-06', size: 0 }),
  // 根目录文件
  makeFile({ id: 'f10', name: '摩托车发动机维修手册.pdf', type: 'pdf', size: 18432000, ext: 'pdf', category: '手册', uploader: '张工', equipmentId: 'eq1', equipmentName: 'CG-125发动机', inKnowledgeBase: true, parseStatus: 'done', starred: true, tags: ['发动机', '手册'], updateTime: '2026-06-10 08:30', readContent: '摩托车发动机维修手册\n\n第一章 发动机结构\n1.1 气缸体与活塞组\n气缸体是发动机的核心部件，承受高温高压。活塞在气缸内往复运动，通过连杆将直线运动转化为旋转运动。\n\n1.2 配气机构\n配气机构控制进排气门的开闭时序，直接影响发动机的充气效率和排放性能。气门间隙的标准值为0.05-0.10mm。\n\n1.3 点火系统\n点火系统由火花塞、点火线圈、ECU组成。火花塞电极间隙标准值为0.6-0.7mm。\n\n第二章 日常维护\n2.1 机油检查\n每次使用前检查机油液位，确保在上下刻度线之间。每3000公里更换一次机油。\n\n2.2 空气滤清器\n每5000公里清洁或更换空气滤清器。灰尘大的环境下应缩短保养周期。' }),
  makeFile({ id: 'f11', name: 'ZK-320配电柜维护规范.pdf', type: 'pdf', size: 5242880, ext: 'pdf', category: '手册', uploader: '李工', equipmentId: 'eq2', equipmentName: '配电柜 ZK-320', inKnowledgeBase: true, parseStatus: 'done', tags: ['配电柜', '规范'], updateTime: '2026-06-09 14:20', readContent: 'ZK-320配电柜维护规范\n\n一、巡检要点\n1. 检查柜体外观，无变形、腐蚀\n2. 检查指示灯状态，绿灯正常、红灯告警\n3. 使用红外测温仪检测各接点温度\n4. 正常运行温度不应超过65℃\n\n二、定期维护\n2.1 月度维护\n- 清理柜内灰尘\n- 紧固各接线端子\n- 检查断路器分合闸状态\n\n2.2 年度维护\n- 全面检测绝缘电阻\n- 校验保护装置\n- 更换老化部件' }),
  makeFile({ id: 'f12', name: '发动机异响现场照片.jpg', type: 'image', size: 2097152, ext: 'jpg', category: '附件', uploader: '王工', taskId: 't2', taskTitle: 'CG-125发动机异响排查', equipmentId: 'eq1', thumbnail: '/static/equipment.png', tags: ['异响', '现场'], parseStatus: 'pending', updateTime: '2026-06-10 10:15', readContent: '【图片预览】发动机异响现场照片\n\n拍摄时间：2026-06-10 10:15\n拍摄人：王工\n关联任务：CG-125发动机异响排查\n\n图片说明：\n现场拍摄的发动机气门区域照片，可观察到气门间隙偏大的迹象。照片中可见气门摇臂与凸轮轴之间的间隙明显超出标准值。' }),
  makeFile({ id: 'f13', name: '配电柜过热红外图.jpg', type: 'image', size: 3145728, ext: 'jpg', category: '附件', uploader: '张工', taskId: 't1', taskTitle: 'ZK-320配电柜过热检修', equipmentId: 'eq2', thumbnail: '/static/equipment.png', tags: ['过热', '红外'], parseStatus: 'done', updateTime: '2026-06-10 09:45', readContent: '【图片预览】配电柜过热红外热成像图\n\n拍摄时间：2026-06-10 09:45\n拍摄人：张工\n关联任务：ZK-320配电柜过热检修\n\n红外分析：\n- A相接触器触点温度：85℃（红色高温区）\n- B相接触器触点温度：52℃（正常）\n- C相接触器触点温度：48℃（正常）\n- 环境温度：28℃\n\n结论：A相触点存在接触不良，需重点检查。' }),
  makeFile({ id: 'f14', name: '点火系统检查流程.docx', type: 'document', size: 1048576, ext: 'docx', category: '流程', uploader: '李工', inKnowledgeBase: true, parseStatus: 'done', tags: ['点火', '流程'], updateTime: '2026-06-08 16:00', readContent: '点火系统检查流程\n\n适用设备：CG-125摩托车发动机\n检修等级：一级检修\n预计工时：30分钟\n\n步骤1：安全确认\n- 发动机熄火，钥匙拔出\n- 等待发动机冷却至常温\n\n步骤2：拆卸火花塞\n- 使用火花塞扳手逆时针旋出\n- 检查火花塞型号是否匹配（CR7HSA）\n\n步骤3：检查火花塞状态\n- 电极间隙：标准0.6-0.7mm\n- 电极颜色：棕红色为正常，黑色为积碳，白色为过热\n- 绝缘体：无裂纹、无积碳\n\n步骤4：检查点火线圈\n- 初级线圈电阻：0.5-1.5Ω\n- 次级线圈电阻：5-15kΩ\n- 线圈外观无破损、无烧蚀\n\n步骤5：检查高压线\n- 高压线无破损、无老化\n- 插头连接牢固\n\n步骤6：组装测试\n- 按标准力矩拧紧火花塞（15N·m）\n- 启动发动机，观察点火是否正常' }),
  makeFile({ id: 'f15', name: '2026年6月检修报告汇总.pdf', type: 'report', size: 4194304, ext: 'pdf', category: '报告', uploader: '赵工', parseStatus: 'pending', tags: ['报告', '月报'], updateTime: '2026-06-07 17:30', readContent: '2026年6月检修报告汇总\n\n报告期间：2026-06-01 至 2026-06-07\n编制人：赵工\n\n一、本月检修概况\n- 总检修任务：28项\n- 完成任务：24项（完成率85.7%）\n- 进行中：3项\n- 待处理：1项\n\n二、故障类型分布\n- 电气系统故障：12项（42.9%）\n- 机械系统故障：8项（28.6%）\n- 液压系统故障：5项（17.9%）\n- 其他：3项（10.7%）\n\n三、重点故障\n1. ZK-320配电柜过热（已完成）\n2. CG-125发动机异响（进行中）\n3. 液压千斤顶漏油（已完成）\n\n四、下月计划\n- 完成剩余3项检修任务\n- 更新设备维护周期计划\n- 开展安全培训' }),
  makeFile({ id: 'f16', name: '液压系统泄漏排查视频.mp4', type: 'video', size: 52428800, ext: 'mp4', category: '附件', uploader: '王工', taskId: 't4', taskTitle: '液压千斤顶漏油处理', equipmentId: 'eq3', parseStatus: 'none', tags: ['液压', '视频'], updateTime: '2026-06-06 11:00', readContent: '【视频预览】液压系统泄漏排查\n\n时长：5分32秒\n拍摄人：王工\n关联任务：液压千斤顶漏油处理\n\n视频内容：\n00:00-01:30  漏油现象展示\n01:30-03:00  油封拆卸过程\n03:00-04:30  新密封件安装\n04:30-05:32  测试验证（50次升降无渗漏）' }),
  makeFile({ id: 'f17', name: '万用表校准记录表.xlsx', type: 'document', size: 524288, ext: 'xlsx', category: '附件', uploader: '王工', equipmentId: 'eq4', parseStatus: 'none', tags: ['校准', '记录'], updateTime: '2026-06-05 15:00', readContent: '万用表校准记录表\n\n设备名称：数字万用表\n设备型号：UT61E\n设备编号：EQ-MULTI-004\n校准日期：2026-06-05\n校准人：王工\n\n校准项目及结果：\n┌──────────┬──────────┬──────────┬──────┐\n│ 测量项目 │ 标准值   │ 测量值   │ 误差 │\n├──────────┼──────────┼──────────┼──────┤\n│ 直流电压 │ 10.000V  │ 10.002V  │ +0.02%│\n│ 交流电压 │ 220.0V   │ 219.8V   │ -0.09%│\n│ 直流电流 │ 1.000A   │ 0.999A   │ -0.10%│\n│ 电阻     │ 10.00kΩ  │ 10.01kΩ  │ +0.10%│\n└──────────┴──────────┴──────────┴──────┘\n\n校准结论：合格\n下次校准日期：2027-06-05' }),
  // 设备手册子目录文件
  makeFile({ id: 'f20', name: 'CG-125发动机结构图.png', type: 'image', size: 4194304, ext: 'png', parentId: 'f1', category: '手册', uploader: '张工', equipmentId: 'eq1', thumbnail: '/static/equipment.png', parseStatus: 'done', tags: ['结构图'], updateTime: '2026-06-04 10:00', readContent: '【图片预览】CG-125发动机结构图\n\n图示说明：\n1. 气缸体总成\n2. 活塞组（活塞+活塞环+活塞销）\n3. 连杆\n4. 曲轴\n5. 配气机构（凸轮轴+气门+摇臂）\n6. 点火系统（火花塞+点火线圈）\n7. 燃油供给系统（化油器+油管）\n8. 润滑系统（机油泵+油道）\n9. 冷却系统（散热片）' }),
  makeFile({ id: 'f21', name: 'CG-125故障代码表.pdf', type: 'pdf', size: 2097152, ext: 'pdf', parentId: 'f1', category: '手册', uploader: '张工', equipmentId: 'eq1', inKnowledgeBase: true, parseStatus: 'done', tags: ['故障代码'], updateTime: '2026-06-03 09:00', readContent: 'CG-125故障代码表\n\nE-001  发动机过热\n原因：冷却系统故障、机油不足、长时间高负荷运行\n处理：检查机油液位、清理散热片、降低负荷\n\nE-002  点火系统故障\n原因：火花塞积碳、点火线圈损坏、线路接触不良\n处理：更换火花塞、检查点火线圈、检查线路\n\nE-003  燃油供给异常\n原因：化油器堵塞、油路漏气、油箱通气孔堵塞\n处理：清洗化油器、检查油路、清理通气孔\n\nE-004  润滑系统报警\n原因：机油泵故障、油道堵塞、机油品质劣化\n处理：检查机油泵、清理油道、更换机油\n\nE-005  异常振动\n原因：曲轴轴承磨损、连杆变形、飞轮松动\n处理：检查轴承、校正连杆、紧固飞轮' }),
  // 故障案例子目录
  makeFile({ id: 'f30', name: '启动困难案例-20260501.docx', type: 'document', size: 1572864, ext: 'docx', parentId: 'f2', category: '案例', uploader: '李工', equipmentId: 'eq1', inKnowledgeBase: true, parseStatus: 'done', tags: ['启动', '案例'], updateTime: '2026-05-01 14:00', readContent: 'CG-125发动机启动困难案例\n\n日期：2026-05-01\n检修人：李工\n\n故障现象：\n发动机启动困难，多次打火才能启动，启动后怠速不稳，有轻微抖动。\n\n排查过程：\n1. 检查火花塞 → 电极积碳严重，间隙偏大（0.9mm，标准0.6-0.7mm）\n2. 检查点火线圈 → 初级线圈电阻正常（1.5Ω），次级线圈电阻偏高（18kΩ，标准5-15kΩ）\n3. 检查燃油供给 → 化油器油面偏低，浮子针阀磨损\n4. 检查气缸压力 → 压缩比偏低（8.5:1，标准9.2:1）\n\n处理方案：\n1. 更换火花塞（NGK CR7HSA）\n2. 更换点火线圈\n3. 更换化油器浮子针阀\n4. 更换活塞环（恢复压缩比）\n5. 调整怠速至1400±100rpm\n\n处理结果：\n启动恢复正常，怠速稳定，压缩比恢复至9.0:1。' }),
  makeFile({ id: 'f31', name: '轴承异响案例-20260515.docx', type: 'document', size: 2097152, ext: 'docx', parentId: 'f2', category: '案例', uploader: '王工', equipmentId: 'eq1', parseStatus: 'parsing', tags: ['轴承', '异响'], updateTime: '2026-05-15 16:30', readContent: '发动机轴承异响案例\n\n日期：2026-05-15\n检修人：王工\n\n故障现象：\n发动机运转时发出持续的"嗡嗡"声，转速越高声音越明显，伴有轻微振动。\n\n排查过程：\n1. 使用听诊器定位 → 异响来自曲轴箱下部\n2. 检查机油 → 油质正常，液位正常\n3. 拆卸检查 → 曲轴主轴承表面有明显磨损痕迹\n4. 测量轴承间隙 → 0.08mm（标准0.02-0.05mm）\n\n处理方案：\n1. 更换曲轴主轴承（全套）\n2. 更换连杆轴承\n3. 检查曲轴轴颈磨损情况\n4. 更换机油和机油滤清器\n\n处理结果：\n异响消除，振动恢复正常，轴承间隙恢复至0.03mm。' }),
]

export default {
  name: 'FileExplorer',
  data() {
    return {
      searchText: '',
      searchFocused: false,
      currentFolder: null,
      files: [...MOCK_FILES],
      batchMode: false,
      selectedIds: [],
      sortBy: 'updateTime',
      sortDir: 'desc',
      typeFilter: '',
      activeQuickCat: '',
      loading: false,
      detailFile: null,
      readerMode: false,
      menuFile: null,
      showNewFolder: false,
      newFolderName: '',
      quickCategories: [],
    }
  },
  computed: {
    breadcrumbs() {
      const path = [{ id: null, name: '全部文件' }]
      if (this.currentFolder) {
        const folder = this.files.find(f => f.id === this.currentFolder)
        if (folder) path.push({ id: folder.id, name: folder.name })
      }
      return path
    },
    recentFiles() {
      return [...this.files].filter(f => f.type !== 'folder').sort((a, b) => b.updateTime.localeCompare(a.updateTime)).slice(0, 8)
    },
    displayFiles() {
      let list = this.files.filter(f => f.parentId === this.currentFolder)
      if (this.searchText) {
        const kw = this.searchText.toLowerCase()
        list = this.files.filter(f => f.name.toLowerCase().includes(kw) || (f.tags || []).some(t => t.toLowerCase().includes(kw)))
      }
      if (this.activeQuickCat) {
        list = this.files.filter(f => f.category === this.activeQuickCat)
      }
      if (this.typeFilter) {
        const typeMap = { '图片': 'image', 'PDF': 'pdf', '视频': 'video', '文档': 'document', '报告': 'report', '文件夹': 'folder' }
        const targetType = typeMap[this.typeFilter]
        if (targetType) list = list.filter(f => f.type === targetType)
      }
      // 排序：文件夹优先，然后按排序字段
      list.sort((a, b) => {
        if (a.type === 'folder' && b.type !== 'folder') return -1
        if (a.type !== 'folder' && b.type === 'folder') return 1
        const dir = this.sortDir === 'desc' ? -1 : 1
        const va = a[this.sortBy] || ''
        const vb = b[this.sortBy] || ''
        return va > vb ? dir : va < vb ? -dir : 0
      })
      return list
    },
    sortIcon() { return this.sortDir === 'desc' ? '↓' : '↑' },
    sortLabel() {
      const labels = { updateTime: '时间', name: '名称', size: '大小' }
      return labels[this.sortBy] || '时间'
    },
  },
  mounted() {
    const cats = new Set()
    this.files.forEach(f => { if (f.category && f.type !== 'folder') cats.add(f.category) })
    this.quickCategories = [...cats].map(c => ({ key: c, label: c }))
  },
  methods: {
    onSearch() { /* computed 自动响应 */ },
    toggleQuickCat(key) {
      this.activeQuickCat = this.activeQuickCat === key ? '' : key
      this.currentFolder = null
    },
    cycleSort() {
      const fields = ['updateTime', 'name', 'size']
      const idx = fields.indexOf(this.sortBy)
      if (idx === fields.length - 1 && this.sortDir === 'desc') {
        this.sortBy = fields[0]
        this.sortDir = 'desc'
      } else if (this.sortDir === 'desc') {
        this.sortDir = 'asc'
      } else {
        this.sortBy = fields[(idx + 1) % fields.length]
        this.sortDir = 'desc'
      }
    },
    cycleTypeFilter() {
      const types = ['', '图片', 'PDF', '视频', '文档', '报告', '文件夹']
      const idx = types.indexOf(this.typeFilter)
      this.typeFilter = types[(idx + 1) % types.length]
    },
    onItemClick(f) {
      if (this.batchMode) { this.toggleSelect(f.id); return }
      if (f.type === 'folder') { this.currentFolder = f.id; return }
      this.openWithSystem(f)
    },
    openFile(f) {
      this.onItemClick(f)
    },
    openWithSystem(f) {
      const ext = (f.ext || '').toLowerCase()
      const isPDF = ext === 'pdf'
      const isDoc = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'].includes(ext)

      // 有本地文件路径 → 用系统打开
      if (f.filePath) {
        this._openNative(f.filePath, ext)
        return
      }

      // 有远程URL → 下载后打开
      if (f.url) {
        this._downloadAndOpen(f.url, ext)
        return
      }

      // PDF文件 → 尝试在新窗口打开 static/manuals/ 下的真实文件
      if (isPDF) {
        const staticPath = `/static/manuals/${f.name}`
        // #ifdef H5
        window.open(staticPath, '_blank')
        return
        // #endif
        // #ifndef H5
        this._openNative(staticPath, ext)
        return
        // #endif
      }

      // doc/xls/ppt → 提示下载或用文本预览
      if (isDoc) {
        uni.showModal({
          title: '打开文件',
          content: `是否使用 WPS 打开「${f.name}」？\n\n如设备未安装 WPS，将显示文本预览。`,
          confirmText: 'WPS打开',
          cancelText: '文本预览',
          success: (res) => {
            if (res.confirm) {
              uni.showToast({ title: '请在真机环境中使用WPS打开', icon: 'none', duration: 2000 })
            } else {
              this.$emit('open-reader', f)
            }
          }
        })
        return
      }

      // 图片 → 新窗口查看
      if (f.type === 'image' && f.thumbnail) {
        // #ifdef H5
        window.open(f.thumbnail, '_blank')
        return
        // #endif
      }

      // 其他 → 文本预览
      this.$emit('open-reader', f)
    },
    _openNative(filePath, ext) {
      const fileTypeMap = {
        pdf: 'pdf', doc: 'doc', docx: 'docx', xls: 'xls', xlsx: 'xlsx',
        ppt: 'ppt', pptx: 'pptx', txt: 'txt', csv: 'csv'
      }
      uni.openDocument({
        filePath: filePath,
        fileType: fileTypeMap[ext] || undefined,
        showMenu: true,
        fail: () => {
          this.$emit('open-reader', this.detailFile || {})
          uni.showToast({ title: '无法打开文件，已切换为文本预览', icon: 'none' })
        }
      })
    },
    _downloadAndOpen(url, ext) {
      uni.showLoading({ title: '正在下载...', mask: true })
      uni.downloadFile({
        url: url,
        success: (res) => {
          uni.hideLoading()
          if (res.statusCode === 200) {
            this._openNative(res.tempFilePath, ext)
          } else {
            uni.showToast({ title: '下载失败', icon: 'none' })
          }
        },
        fail: () => {
          uni.hideLoading()
          uni.showToast({ title: '下载失败，请检查网络', icon: 'none' })
        }
      })
    },
    closeDetail() {
      this.readerMode = false
      this.detailFile = null
    },
    onItemLongPress(f) {
      if (!this.batchMode) this.menuFile = f
    },
    navigateTo(id) { this.currentFolder = id },
    toggleSelect(id) {
      const idx = this.selectedIds.indexOf(id)
      if (idx >= 0) this.selectedIds.splice(idx, 1)
      else this.selectedIds.push(id)
    },
    showFileMenu(f) { this.menuFile = f },
    toggleStar(f) { f.starred = !f.starred },
    addToKB(f) {
      f.inKnowledgeBase = true
      f.parseStatus = 'pending'
      uni.showToast({ title: '已加入知识库', icon: 'success' })
    },
    renameFile(f) {
      this.menuFile = null
      uni.showModal({
        title: '重命名',
        editable: true,
        placeholderText: f.name,
        success: (res) => {
          if (res.confirm && res.content) f.name = res.content
        }
      })
    },
    moveFile(f) { this.menuFile = null; uni.showToast({ title: '请选择目标文件夹', icon: 'none' }) },
    deleteFile(f) {
      this.menuFile = null
      uni.showModal({
        title: '确认删除', content: `确定删除「${f.name}」？`,
        success: (res) => {
          if (res.confirm) {
            this.files = this.files.filter(file => file.id !== f.id)
            this.detailFile = null
            uni.showToast({ title: '已删除', icon: 'none' })
          }
        }
      })
    },
    batchAddToKB() {
      this.selectedIds.forEach(id => {
        const f = this.files.find(x => x.id === id)
        if (f && f.type !== 'folder') { f.inKnowledgeBase = true; f.parseStatus = 'pending' }
      })
      uni.showToast({ title: `已加入 ${this.selectedIds.length} 个文件`, icon: 'success' })
      this.selectedIds = []; this.batchMode = false
    },
    batchMove() { uni.showToast({ title: '批量移动功能开发中', icon: 'none' }) },
    batchDelete() {
      uni.showModal({
        title: '批量删除', content: `确定删除 ${this.selectedIds.length} 个文件？`,
        success: (res) => {
          if (res.confirm) {
            this.files = this.files.filter(f => !this.selectedIds.includes(f.id))
            this.selectedIds = []; this.batchMode = false
            uni.showToast({ title: '已删除', icon: 'none' })
          }
        }
      })
    },
    createFolder() {
      if (!this.newFolderName.trim()) return
      this.files.push(makeFile({
        name: this.newFolderName.trim(),
        type: 'folder',
        parentId: this.currentFolder,
        category: '附件',
      }))
      this.newFolderName = ''
      this.showNewFolder = false
      uni.showToast({ title: '文件夹已创建', icon: 'success' })
    },
    loadMore() { /* 分页加载 */ },
    getTypeIcon(type) {
      return { folder: '📁', pdf: '📕', image: '🖼️', video: '🎬', document: '📝', report: '📊' }[type] || '📄'
    },
    getTypeBg(type) {
      return { folder: '#EFF6FF', pdf: '#FEF2F2', image: '#F0FDF4', video: '#FDF2F8', document: '#FFFBEB', report: '#F5F3FF' }[type] || '#F1F5F9'
    },
    parseLabel(s) {
      return { none: '未解析', pending: '等待中', parsing: '解析中', done: '已完成', failed: '失败' }[s] || '未知'
    },
    formatSize(bytes) {
      if (!bytes) return '--'
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
      if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB'
      return (bytes / 1073741824).toFixed(1) + ' GB'
    },
    formatTime(t) {
      if (!t) return ''
      return t.replace(/T/g, ' ').slice(0, 16)
    },
  }
}
</script>

<style scoped>
.fe-root {
  display: flex; flex-direction: column; height: 100%;
  background: linear-gradient(180deg, #F0F4FA 0%, #F8FAFC 100%);
}

/* 工具栏 */
.fe-toolbar {
  display: flex; align-items: center; gap: 16rpx;
  padding: 16rpx 20rpx;
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFF 100%);
  border-bottom: 1rpx solid rgba(0,0,0,0.04);
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.03);
}
.fe-search {
  flex: 1; display: flex; align-items: center;
  background: #F1F5F9; border-radius: 28rpx;
  padding: 0 20rpx; height: 72rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
  box-shadow: inset 0 1rpx 4rpx rgba(0,0,0,0.04);
}
.fe-search.focused {
  border-color: #3B82F6; background: #FFFFFF;
  box-shadow: 0 0 0 4rpx rgba(59,130,246,0.1), inset 0 1rpx 4rpx rgba(0,0,0,0.02);
}
.fe-search-icon { font-size: 28rpx; margin-right: 10rpx; }
.fe-search-input { flex: 1; font-size: 28rpx; color: #1E293B; }
.fe-search-clear { font-size: 28rpx; color: #94A3B8; padding: 8rpx; }
.fe-actions { display: flex; gap: 12rpx; }
.fe-action-btn {
  width: 72rpx; height: 72rpx; border-radius: 20rpx;
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(59,130,246,0.1);
  transition: all 0.2s ease;
}
.fe-action-btn:active { transform: scale(0.92); box-shadow: 0 1rpx 4rpx rgba(59,130,246,0.15); }
.fe-action-icon { font-size: 28rpx; }

/* 面包屑 */
.fe-breadcrumb {
  display: flex; align-items: center;
  padding: 10rpx 20rpx; background: #FFFFFF; gap: 6rpx;
  border-bottom: 1rpx solid rgba(0,0,0,0.03);
}
.fe-crumb { display: flex; align-items: center; gap: 6rpx; }
.fe-crumb-text { font-size: 24rpx; color: #3B82F6; font-weight: 600; }
.fe-crumb-text.active { color: #0F172A; font-weight: 800; }
.fe-crumb-sep { font-size: 20rpx; color: #CBD5E1; }

/* 快捷分类 */
.fe-cats {
  background: #FFFFFF; padding: 16rpx 0;
  border-bottom: 1rpx solid rgba(0,0,0,0.03);
}
.fe-cats-scroll { white-space: nowrap; }
.fe-cats-inner { display: inline-flex; gap: 14rpx; padding: 0 20rpx; }
.fe-cat-chip {
  display: inline-flex; align-items: center; gap: 6rpx;
  padding: 12rpx 24rpx; border-radius: 24rpx;
  background: #F8FAFC; border: 2rpx solid #E2E8F0;
  transition: all 0.25s ease;
}
.fe-cat-chip:active { transform: scale(0.95); }
.fe-cat-chip.active {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  border-color: #3B82F6;
  box-shadow: 0 2rpx 12rpx rgba(59,130,246,0.15);
}
.fe-cat-icon { font-size: 24rpx; }
.fe-cat-label { font-size: 24rpx; color: #475569; font-weight: 600; white-space: nowrap; }
.fe-cat-chip.active .fe-cat-label { color: #2563EB; font-weight: 700; }

/* 子工具条 */
.fe-subbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10rpx 20rpx; background: #FFFFFF;
  border-bottom: 1rpx solid rgba(0,0,0,0.03);
}
.fe-subbar-left, .fe-subbar-right { display: flex; align-items: center; gap: 14rpx; }
.fe-sort-btn, .fe-filter-btn, .fe-batch-btn, .fe-view-toggle {
  display: flex; align-items: center; gap: 6rpx;
  padding: 8rpx 16rpx; border-radius: 10rpx;
  font-size: 22rpx; color: #64748B;
  transition: all 0.2s ease;
}
.fe-sort-btn:active, .fe-filter-btn:active, .fe-batch-btn:active { background: #F1F5F9; }
.fe-filter-btn.active { color: #2563EB; background: #EFF6FF; }
.fe-batch-btn.active { color: #EF4444; background: #FEF2F2; }
.fe-view-toggle { font-size: 30rpx; }

/* 批量操作栏 */
.fe-batch-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12rpx 20rpx;
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  border-bottom: 1rpx solid #BFDBFE;
}
.fe-batch-count { font-size: 24rpx; color: #2563EB; font-weight: 700; }
.fe-batch-actions { display: flex; gap: 12rpx; }
.fe-ba-btn {
  padding: 8rpx 20rpx; border-radius: 10rpx;
  background: #FFFFFF; font-size: 22rpx; color: #475569;
  box-shadow: 0 1rpx 4rpx rgba(0,0,0,0.06);
}
.fe-ba-btn.danger { color: #EF4444; }

/* 最近文件 */
.fe-recent {
  background: #FFFFFF; padding: 20rpx 0 16rpx;
  border-bottom: 1rpx solid rgba(0,0,0,0.03);
}
.fe-section-title {
  font-size: 28rpx; font-weight: 700; color: #0F172A;
  padding: 0 20rpx; display: block; margin-bottom: 14rpx;
}
.fe-recent-scroll { white-space: nowrap; }
.fe-recent-inner { display: inline-flex; gap: 16rpx; padding: 0 20rpx; }
.fe-recent-card {
  display: inline-flex; flex-direction: column;
  align-items: center; gap: 8rpx;
  width: 160rpx; padding: 16rpx 10rpx;
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  border-radius: 16rpx; border: 1rpx solid #E2E8F0;
  transition: all 0.2s ease;
}
.fe-recent-card:active { transform: scale(0.95); opacity: 0.8; }
.fe-recent-icon-wrap { width: 72rpx; height: 72rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; }
.fe-recent-icon { font-size: 34rpx; }
.fe-recent-name { font-size: 20rpx; color: #1E293B; font-weight: 600; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 145rpx; }
.fe-recent-time { font-size: 18rpx; color: #94A3B8; }

/* 列表视图 */
.fe-list-scroll { flex: 1; }
.fe-list { padding: 12rpx 20rpx; }
.fe-list-item {
  display: flex; align-items: center; gap: 16rpx;
  padding: 20rpx; background: #FFFFFF;
  border-radius: 16rpx; margin-bottom: 12rpx;
  border: 1rpx solid rgba(0,0,0,0.04);
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
  transition: all 0.25s ease;
}
.fe-list-item:active { transform: scale(0.99); background: #F8FAFC; }
.fe-list-item.selected {
  border-color: #3B82F6; background: #EFF6FF;
  box-shadow: 0 2rpx 12rpx rgba(59,130,246,0.12);
}
.fe-checkbox { padding: 4rpx; }
.fe-check-icon { font-size: 30rpx; color: #3B82F6; }
.fe-item-icon-wrap {
  width: 64rpx; height: 64rpx; border-radius: 16rpx;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
}
.fe-item-icon { font-size: 30rpx; }
.fe-item-info { flex: 1; min-width: 0; }
.fe-item-name-row { display: flex; align-items: center; gap: 8rpx; }
.fe-item-name { font-size: 28rpx; font-weight: 700; color: #0F172A; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fe-star { font-size: 24rpx; flex-shrink: 0; }
.fe-item-meta-row { display: flex; gap: 14rpx; margin-top: 6rpx; }
.fe-item-meta { font-size: 20rpx; color: #94A3B8; }
.fe-item-tags { display: flex; gap: 8rpx; margin-top: 8rpx; align-items: center; flex-wrap: wrap; }
.fe-item-tag {
  font-size: 18rpx; color: #475569; background: #F1F5F9;
  padding: 4rpx 12rpx; border-radius: 8rpx;
}
.fe-parse-badge { font-size: 18rpx; padding: 4rpx 12rpx; border-radius: 8rpx; font-weight: 600; margin-left: 4rpx; }
.parse-none { color: #94A3B8; background: #F1F5F9; }
.parse-pending { color: #D97706; background: #FFFBEB; }
.parse-parsing { color: #2563EB; background: #EFF6FF; }
.parse-done { color: #16A34A; background: #F0FDF4; }
.parse-failed { color: #EF4444; background: #FEF2F2; }
.fe-item-more { padding: 8rpx; }
.fe-more-icon { font-size: 30rpx; color: #94A3B8; }

/* 网格视图 */
.fe-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16rpx; padding: 16rpx 20rpx; }
.fe-grid-item {
  display: flex; flex-direction: column; align-items: center; gap: 10rpx;
  padding: 24rpx 10rpx; background: #FFFFFF;
  border-radius: 16rpx; border: 1rpx solid rgba(0,0,0,0.04);
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
  transition: all 0.2s ease;
}
.fe-grid-item:active { transform: scale(0.96); }
.fe-grid-icon-wrap { width: 80rpx; height: 80rpx; border-radius: 20rpx; display: flex; align-items: center; justify-content: center; position: relative; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06); }
.fe-grid-icon { font-size: 40rpx; }
.fe-grid-name { font-size: 22rpx; color: #1E293B; font-weight: 600; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 100%; }
.fe-grid-meta { font-size: 18rpx; color: #94A3B8; }

/* 空状态 */
.fe-empty { display: flex; flex-direction: column; align-items: center; padding: 100rpx 0; gap: 20rpx; }
.fe-empty-icon { font-size: 80rpx; }
.fe-empty-text { font-size: 28rpx; color: #94A3B8; font-weight: 500; }
.fe-empty-btn {
  margin-top: 12rpx; padding: 20rpx 48rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(37,99,235,0.3);
}
.fe-empty-btn:active { transform: scale(0.96); }
.fe-empty-btn-text { font-size: 28rpx; color: #FFFFFF; font-weight: 700; }

/* 加载状态 */
.fe-loading { display: flex; align-items: center; justify-content: center; padding: 40rpx; gap: 14rpx; }
.fe-loading-spinner { width: 36rpx; height: 36rpx; border: 4rpx solid #E2E8F0; border-top-color: #3B82F6; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.fe-loading-text { font-size: 24rpx; color: #94A3B8; }

/* 文件详情弹窗 */
.fe-detail-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 2000;
  display: flex; align-items: flex-end;
  backdrop-filter: blur(4px);
}
.fe-detail-panel {
  width: 100%; max-height: 85vh; background: #FFFFFF;
  border-radius: 28rpx 28rpx 0 0;
  display: flex; flex-direction: column;
  box-shadow: 0 -8rpx 40rpx rgba(0,0,0,0.1);
}
.fe-detail-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 28rpx; border-bottom: 1rpx solid #F1F5F9; flex-shrink: 0;
}
.fe-detail-title { font-size: 34rpx; font-weight: 800; color: #0F172A; }
.fe-detail-close { font-size: 40rpx; color: #64748B; padding: 8rpx 16rpx; font-weight: 700; }
.fe-detail-body { flex: 1; overflow-y: auto; }
.fe-preview-area { display: flex; align-items: center; justify-content: center; padding: 40rpx; background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); }
.fe-preview-icon-wrap { width: 88rpx; height: 88rpx; border-radius: 24rpx; display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08); }
.fe-preview-icon { font-size: 44rpx; }
.fe-preview-img { width: 300rpx; height: 200rpx; border-radius: 16rpx; margin-left: 16rpx; }
.fe-info-list { padding: 0 28rpx; }
.fe-info-row { display: flex; justify-content: space-between; align-items: center; padding: 18rpx 0; border-bottom: 1rpx solid #F8FAFC; }
.fe-info-label { font-size: 26rpx; color: #94A3B8; }
.fe-info-value { font-size: 26rpx; color: #1E293B; font-weight: 600; max-width: 60%; text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fe-info-value.link { color: #3B82F6; }
.parse-text-done { color: #16A34A; }
.parse-text-pending { color: #D97706; }
.parse-text-parsing { color: #2563EB; }
.parse-text-failed { color: #EF4444; }
.fe-detail-actions { display: flex; flex-wrap: wrap; gap: 14rpx; padding: 28rpx; }
.fe-da-btn {
  flex: 1; min-width: 45%; padding: 18rpx;
  background: #F8FAFC; border-radius: 14rpx;
  text-align: center; font-size: 26rpx; color: #475569;
  border: 1rpx solid #E2E8F0;
  transition: all 0.2s ease;
}
.fe-da-btn:active { background: #F1F5F9; transform: scale(0.97); }
.fe-da-btn.danger { color: #EF4444; border-color: #FEE2E2; }
.fe-da-btn.primary { background: #EFF6FF; color: #2563EB; border-color: #BFDBFE; }
.fe-detail-close-bar {
  padding: 28rpx; text-align: center;
  border-top: 1rpx solid #F1F5F9;
  background: #F8FAFC; border-radius: 0 0 28rpx 28rpx; flex-shrink: 0;
}
.fe-detail-close-bar:active { background: #F1F5F9; }
.fe-detail-close-bar-text { font-size: 30rpx; color: #475569; font-weight: 700; }

/* 阅读模式 */
.fe-reader-body { flex: 1; padding: 28rpx; }
.fe-reader-meta { margin-bottom: 24rpx; padding-bottom: 18rpx; border-bottom: 1rpx solid #F1F5F9; }
.fe-reader-source { font-size: 24rpx; color: #94A3B8; display: block; margin-bottom: 10rpx; }
.fe-reader-tags { display: flex; gap: 10rpx; flex-wrap: wrap; }
.fe-reader-tag { font-size: 22rpx; color: #2563EB; background: #EFF6FF; padding: 6rpx 16rpx; border-radius: 8rpx; }
.fe-reader-content { font-size: 28rpx; color: #334155; line-height: 1.9; white-space: pre-wrap; }

/* 新建文件夹弹窗 */
.fe-modal-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 2000;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}
.fe-modal-box { width: 82%; background: #FFFFFF; border-radius: 20rpx; padding: 36rpx; box-shadow: 0 8rpx 40rpx rgba(0,0,0,0.12); }
.fe-modal-title { font-size: 34rpx; font-weight: 800; color: #0F172A; display: block; margin-bottom: 28rpx; }
.fe-modal-input { width: 100%; height: 84rpx; border: 2rpx solid #E2E8F0; border-radius: 14rpx; padding: 0 20rpx; font-size: 28rpx; margin-bottom: 28rpx; background: #F8FAFC; }
.fe-modal-btns { display: flex; gap: 16rpx; }
.fe-mbtn { flex: 1; padding: 22rpx; border-radius: 14rpx; text-align: center; font-size: 28rpx; font-weight: 700; }
.fe-mbtn.cancel { background: #F1F5F9; color: #64748B; }
.fe-mbtn.confirm { background: linear-gradient(135deg, #3B82F6, #2563EB); color: #FFFFFF; box-shadow: 0 4rpx 16rpx rgba(37,99,235,0.3); }

/* 文件操作菜单 */
.fe-menu-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 2000;
  display: flex; align-items: flex-end;
  backdrop-filter: blur(4px);
}
.fe-menu-panel { width: 100%; background: #FFFFFF; border-radius: 28rpx 28rpx 0 0; padding: 20rpx 0; box-shadow: 0 -8rpx 40rpx rgba(0,0,0,0.1); }
.fe-menu-item { padding: 28rpx 36rpx; font-size: 30rpx; color: #1E293B; transition: background 0.15s; }
.fe-menu-item:active { background: #F1F5F9; }
.fe-menu-item.danger { color: #EF4444; }
.fe-menu-cancel { padding: 28rpx 36rpx; font-size: 30rpx; color: #94A3B8; text-align: center; border-top: 1rpx solid #F1F5F9; margin-top: 10rpx; }

/* 上传弹窗 */
.fe-upload-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 2000;
  display: flex; align-items: flex-end;
  backdrop-filter: blur(4px);
}
.fe-upload-panel {
  width: 100%; max-height: 90vh; background: #FFFFFF;
  border-radius: 28rpx 28rpx 0 0;
  display: flex; flex-direction: column;
  box-shadow: 0 -8rpx 40rpx rgba(0,0,0,0.1);
}
.fe-upload-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 28rpx; border-bottom: 1rpx solid #F1F5F9;
}
.fe-upload-title { font-size: 34rpx; font-weight: 800; color: #0F172A; }
.fe-upload-close { font-size: 36rpx; color: #94A3B8; padding: 8rpx; }
.fe-upload-body { padding: 28rpx; overflow-y: auto; flex: 1; }
.fe-upload-drop {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 48rpx; border: 3rpx dashed #CBD5E1;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  margin-bottom: 28rpx; gap: 10rpx;
  transition: all 0.2s ease;
}
.fe-upload-drop:active { background: #EFF6FF; border-color: #3B82F6; }
.fe-upload-drop-icon { font-size: 52rpx; }
.fe-upload-drop-text { font-size: 28rpx; color: #475569; font-weight: 700; }
.fe-upload-drop-hint { font-size: 22rpx; color: #94A3B8; }
.fe-uf-group { margin-bottom: 24rpx; }
.fe-uf-label { font-size: 24rpx; color: #64748B; font-weight: 700; display: block; margin-bottom: 10rpx; }
.fe-uf-chips { display: flex; flex-wrap: wrap; gap: 12rpx; }
.fe-uf-chip {
  padding: 10rpx 24rpx; border-radius: 12rpx;
  background: #F1F5F9; font-size: 24rpx; color: #475569;
  border: 2rpx solid #E2E8F0;
  transition: all 0.2s ease;
}
.fe-uf-chip.active { background: #EFF6FF; border-color: #3B82F6; color: #2563EB; font-weight: 700; }
.fe-uf-input { width: 100%; height: 76rpx; border: 2rpx solid #E2E8F0; border-radius: 14rpx; padding: 0 20rpx; font-size: 26rpx; background: #F8FAFC; }
.fe-uf-select {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18rpx; background: #F8FAFC;
  border-radius: 14rpx; border: 2rpx solid #E2E8F0;
}
.fe-uf-select-text { font-size: 26rpx; color: #475569; }
.fe-uf-select-arrow { font-size: 30rpx; color: #CBD5E1; }
.fe-uf-row { display: flex; align-items: center; justify-content: space-between; }
.fe-uf-switch { width: 84rpx; height: 46rpx; border-radius: 23rpx; background: #CBD5E1; padding: 4rpx; transition: background 0.25s; }
.fe-uf-switch.on { background: #3B82F6; }
.fe-uf-switch-thumb { width: 38rpx; height: 38rpx; border-radius: 50%; background: #FFFFFF; transition: transform 0.25s; box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.1); }
.fe-uf-switch.on .fe-uf-switch-thumb { transform: translateX(38rpx); }
.fe-upload-progress { margin: 20rpx 0; }
.fe-progress-bar { height: 14rpx; background: #E2E8F0; border-radius: 7rpx; overflow: hidden; }
.fe-progress-fill { height: 100%; background: linear-gradient(90deg, #3B82F6, #60A5FA); border-radius: 7rpx; transition: width 0.2s; }
.fe-progress-text { font-size: 22rpx; color: #2563EB; font-weight: 700; text-align: center; display: block; margin-top: 6rpx; }
.fe-upload-error { padding: 14rpx; background: #FEF2F2; border-radius: 12rpx; margin: 10rpx 0; }
.fe-error-text { font-size: 24rpx; color: #EF4444; }
.fe-upload-submit {
  padding: 28rpx;
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  border-radius: 16rpx; text-align: center; margin-top: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(37,99,235,0.3);
}
.fe-upload-submit.disabled { opacity: 0.5; }
.fe-upload-submit:active { transform: scale(0.98); }
.fe-submit-text { font-size: 30rpx; color: #FFFFFF; font-weight: 800; }

/* 选择器弹窗 */
.fe-picker-mask {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 2000;
  display: flex; align-items: flex-end;
  backdrop-filter: blur(4px);
}
.fe-picker-panel {
  width: 100%; max-height: 60vh; background: #FFFFFF;
  border-radius: 28rpx 28rpx 0 0;
  display: flex; flex-direction: column;
  box-shadow: 0 -8rpx 40rpx rgba(0,0,0,0.1);
}
.fe-picker-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 28rpx; border-bottom: 1rpx solid #F1F5F9;
}
.fe-picker-title { font-size: 34rpx; font-weight: 800; color: #0F172A; }
.fe-picker-close { font-size: 36rpx; color: #94A3B8; padding: 8rpx; }
.fe-picker-list { flex: 1; overflow-y: auto; }
.fe-picker-item {
  display: flex; align-items: center; gap: 18rpx;
  padding: 24rpx 28rpx; border-bottom: 1rpx solid #F8FAFC;
  transition: background 0.15s;
}
.fe-picker-item:active { background: #F8FAFC; }
.fe-picker-item-icon { font-size: 30rpx; }
.fe-picker-item-info { flex: 1; }
.fe-picker-item-name { font-size: 28rpx; font-weight: 700; color: #1E293B; display: block; }
.fe-picker-item-sub { font-size: 22rpx; color: #94A3B8; display: block; margin-top: 4rpx; }

</style>
