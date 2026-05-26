<script setup lang="ts">
import FileInput from './components/FileInput.vue'
import { verifyBadge } from './utils/verifyBadge'
import { ref, computed } from 'vue'

const publicKeyPem = `-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAqihA2xS+pIA/DGAqu0lPEPcf8Nv7Zzmhj8freVkLyu0=
-----END PUBLIC KEY-----`;

const verificationResult = ref<boolean | null>(null);
const badgeList = ref<Array<{key: string, value: any}>>([]);
const errorMessage = ref<string>('');
const showUploadSection = ref<boolean>(true);
const showSuccessMessage = ref<boolean>(true);
const showAboutModal = ref<boolean>(false);

const badgeMedia = computed(() => {
  if (!badgeList.value || !verificationResult.value) {
    return null;
  }
  
  // 从badge数据中直接获取image和video的base64数据
  let imageData = '';
  let videoData = '';
  
  for (const item of badgeList.value) {
    if (item.key === 'image') {
      imageData = item.value;
    } else if (item.key === 'video') {
      videoData = item.value;
    }
  }
  
  return {
    image: imageData || null,
    video: videoData || null
  };
});

function toggleUploadSection() {
  showUploadSection.value = !showUploadSection.value;
}

function toggleAboutModal() {
  showAboutModal.value = !showAboutModal.value;
}

// 将英文key转换为中文显示
function getKeyDisplay(key: string): string {
  const keyMap: Record<string, string> = {
    'member_name': '持有人',
    'member_student_id': '学号',
    'member_role': '角色',
    'club_name': '社团',
    'club_id': '社团ID',
    'badge_title': '标题',
    'badge_type': '类型',
    'badge_year': '年份',
    'badge_description': '描述',
    'issue_time': '颁发时间',
    'id': '唯一ID',
    'name': '姓名',
    'student_id': '学号',
    'role': '角色',
    'clubName': '社团',
    'clubId': '社团ID',
    'badgeType': '类型',
    'badgeYear': '年份',
    'badgeDescription': '描述',
    'issueTime': '颁发时间',
    'image': '徽章图片',
    'video': '徽章视频'
  };
  return keyMap[key] || key;
}

async function processJsonFile(file: File) {
  try {
    const text = await file.text();
    const data = JSON.parse(text);

    // 验证签名（badge现在是JSON字符串）
    const isValid = await verifyBadge(data.badge, data.signature, data.algorithm, publicKeyPem);

    // 解析badge字符串为数组
    const badgeArr = JSON.parse(data.badge);

    verificationResult.value = isValid;
    badgeList.value = badgeArr;
    errorMessage.value = '';
    showSuccessMessage.value = true;
    
    if (isValid) {
      showUploadSection.value = false;
      setTimeout(() => {
        showSuccessMessage.value = false;
      }, 2000);
    }
  } catch (error) {
    console.error('Error processing file:', error);
    errorMessage.value = '文件处理错误，请确保选择的是有效的纪念章文件';
    verificationResult.value = null;
    badgeList.value = [];
  }
}
</script>

<template>
  <div class="app-container">
    <!-- 顶部操作按钮组 -->
    <div class="top-buttons">
      <!-- GitHub链接按钮 -->
      <a href="https://github.com/SiliconSiliconGrass/silicon-badge" 
         target="_blank" 
         rel="noopener noreferrer"
         class="github-button"
         title="查看项目源码">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.7-2.782.605-3.369-1.343-3.369-1.343-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.268 2.75 1.026A9.578 9.578 0 0112 6.844c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.026 2.747-1.026.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.138 20.161 22 16.44 22 12.017 22 6.484 17.522 2 12 2z" clip-rule="evenodd"/>
        </svg>
      </a>
      
      <!-- 关于按钮 -->
      <button @click="toggleAboutModal" class="about-button" title="关于项目">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
      </button>
    </div>

    <!-- 展开按钮 - 验证通过后显示 -->
    <button v-if="verificationResult === true && !showUploadSection" 
            @click="toggleUploadSection" 
            class="expand-button">
      <span class="expand-icon">📁</span>
      <span class="expand-text">上传新文件</span>
    </button>

    <!-- 标题和上传区域 - 验证通过时折叠 -->
    <transition name="collapse">
      <div v-show="showUploadSection" class="upload-section">
        <header>
          <h1>验收你的网协纪念章！</h1>
          <p>请选择一个 .json 文件来验证你的纪念章</p>
        </header>

        <FileInput @file-selected="processJsonFile" />

        <!-- 错误信息显示 -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
      </div>
    </transition>

    <!-- 关于项目模态框 -->
    <transition name="modal">
      <div v-if="showAboutModal" class="modal-overlay" @click="toggleAboutModal">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="toggleAboutModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          
          <h2>关于本项目</h2>
          
          <div class="about-content">
            <section>
              <h3>🔐 防伪技术</h3>
              <p>本项目使用<strong>数字签名</strong>技术对纪念章数据进行防伪验证。</p>
              <ul>
                <li>私钥由服务器端保密，确保只有授权机构才能颁发纪念章</li>
                <li>公钥随前端公开，任何人都可以验证纪念章的真实性</li>
                <li>任何对纪念章数据的篡改都会导致验证失败</li>
              </ul>
            </section>
            
            <section>
              <h3>📦 数据结构</h3>
              <p>纪念章文件采用 JSON 格式存储，包含三个核心部分：</p>
              <ul>
                <li><code>badge</code> - 纪念章数据（JSON 字符串形式）</li>
                <li><code>signature</code> - 数字签名</li>
                <li><code>algorithm</code> - 签名算法标识</li>
              </ul>
            </section>
            
            <section>
              <h3>🛡️ 安全特性</h3>
              <ul>
                <li>前端纯本地验证，数据不上传服务器</li>
                <li>支持图片和视频的 Base64 内嵌存储</li>
              </ul>
            </section>
          </div>
        </div>
      </div>
    </transition>

    <!-- 验证结果显示 -->
    <transition name="fade">
      <div v-if="verificationResult !== null" class="verification-result">
        <!-- 成功时的视频背景 -->
        <div v-if="verificationResult && badgeMedia && badgeMedia.video" class="video-background">
          <video 
            :src="badgeMedia.video" 
            class="background-video"
            autoplay 
            loop 
            muted 
            playsinline
          />
        </div>

        <!-- 内容容器 - 确保在视频之上 -->
        <div class="content-wrapper">
          <!-- 验证成功消息 - 始终渲染，保持占位 -->
          <div v-if="verificationResult" :class="['success-message', { 'fade-out': !showSuccessMessage }]">
            <h2>✅ 验证通过！</h2>
            <p>此纪念章真实有效</p>
          </div>
          
          <!-- 验证失败消息 -->
          <transition name="slide-fade">
            <div v-if="!verificationResult" class="error-message">
              <h2>❌ 验证失败！</h2>
              <p>纪念章可能是假的或者已被篡改</p>
              <p>请联系纪念章发放者进行核实</p>
            </div>
          </transition>
          

          <!-- 纪念章信息展示 -->
          <div v-if="badgeList.length > 0" :class="['badge-info', { 'invalid': !verificationResult }]">
            <div class="badge-layout">
              <!-- 左列：纪念章图片和标题 -->
              <div class="badge-left-column">
                <div class="badge-image" :class="{ 'has-image': verificationResult && badgeMedia && badgeMedia.image }">
                  <template v-if="verificationResult && badgeMedia && badgeMedia.image">
                    <img :src="badgeMedia.image" alt="徽章图片" class="badge-img" />
                  </template>
                  <span v-else class="badge-emoji">🏅</span>
                </div>
                <!-- 标题：遍历获取 -->
                <h2 class="badge-title">{{ badgeList.find(i => i.key === 'badge_title' || i.key === '标题' || i.key === 'badgeTitle')?.value || '纪念章' }}</h2>
                <!-- <p class="badge-type">{{ badgeList.find(i => i.key === 'badge_type' || i.key === '类型' || i.key === 'badgeType')?.value || '普通纪念章' }}</p> -->
              </div>
              
              <!-- 右列：详细信息 - 遍历数组，保持顺序 -->
              <div class="badge-right-column">
                <div class="detail-section">
                  <div class="info-grid">
                    <template v-for="item in badgeList.filter(i => i.key !== 'image' && i.key !== 'video')" :key="item.key">
                      <span class="label">{{ getKeyDisplay(item.key) }}</span>
                      <span class="value">{{ item.value || '未设置' }}</span>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.app-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  border-radius: 12px;
  background: #f8fafc;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  position: relative;
  overflow: visible;
}

/* 顶部按钮组 */
.top-buttons {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  z-index: 1000;
}

/* GitHub按钮 */
.github-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #1f2937;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.github-button:hover {
  background: #374151;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

/* 关于按钮 */
.about-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  transition: all 0.3s ease;
}

.about-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.5);
}

/* 展开按钮样式 */
.expand-button {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  transition: all 0.3s ease;
  z-index: 1000;
}

.expand-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.5);
}

.expand-button:active {
  transform: translateY(0);
}

.expand-icon {
  font-size: 1.2rem;
}

.expand-text {
  font-size: 0.95rem;
}

/* 上传区域折叠动画 */
.upload-section {
  transition: all 0.5s ease;
}

.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.5s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  margin-bottom: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  opacity: 1;
  max-height: 500px;
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑动淡出动画 - 用于成功消息 */
.slide-fade-enter-active {
  transition: opacity 0.5s ease-out;
}

.slide-fade-leave-active {
  transition: opacity 0.5s ease-in;
  position: relative;
  pointer-events: none;
}

.slide-fade-enter-from {
  opacity: 0;
}

.slide-fade-leave-to {
  opacity: 0;
}

header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

h1 {
  margin: 0;
  font-size: 2.5rem;
  color: #111827;
  font-weight: 700;
}

p {
  margin: 0.5rem 0 0;
  color: #475569;
  font-size: 1.1rem;
}

.verification-result {
  margin-top: 2rem;
  padding: 2rem;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
  position: relative;
  overflow: hidden;
}

/* 内容容器 - 确保在视频之上 */
.content-wrapper {
  position: relative;
  z-index: 10;
}

.success-message {
  text-align: center;
  color: #10b981;
  margin-bottom: 2rem;
  padding: 1.5rem;
  border-radius: 8px;
  background: #d1fae5;
  transition: opacity 0.5s ease;
}

.success-message.fade-out {
  opacity: 0;
  pointer-events: none;
}

.success-message h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
}

.error-message {
  text-align: center;
  color: #ef4444;
  margin: 1rem 0 2rem;
  padding: 1.5rem;
  border-radius: 8px;
  background: #fee2e2;
}

.error-message h2 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
}

/* 纪念章信息样式 */
.badge-info {
  margin-top: 2rem;
}

.badge-layout {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 3rem;
  align-items: start;
}

/* 左列：纪念章图片和标题 */
.badge-left-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.badge-image {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.badge-emoji {
  font-size: 6rem;
}

.badge-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.badge-image.has-image .badge-img {
  border-radius: 0;
}

.badge-image.has-image {
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

/* 视频背景区域 */
.video-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  overflow: hidden;
  border-radius: 8px;
}

.background-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.1);
  opacity: 0.8;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.7) 0%,
    rgba(255, 255, 255, 0.65) 50%,
    rgba(255, 255, 255, 0.7) 100%
  );
  z-index: 2;
}

.badge-title {
  font-size: 2rem;
  color: #111827;
  font-weight: 700;
}

.badge-type {
  margin: 0;
  font-size: 1.4rem;
  color: #64748b;
  font-weight: 500;
}

/* 右列：详细信息 */
.badge-right-column {
  width: 100%;
}

.detail-section {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.detail-section h3 {
  margin: 0 0 1.5rem;
  font-size: 1.25rem;
  color: #111827;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 4fr;
  gap: 0.5rem 1rem;
  align-items: center;
}

.label {
  font-size: 1.0rem;
  font-weight: 500;
  color: #64748b;
  text-align: right;
}

.value {
  font-size: 1.0rem;
  color: #111827;
  font-weight: 500;
  text-align: left;
}

.full-width {
  grid-column: 1 / -1;
  margin-bottom: 0.5rem;
}

.full-width.label {
  margin-bottom: 0.25rem;
}

.full-width.value {
  text-align: left;
  width: 100%;
}

/* 无效纪念章的样式 */
.badge-info.invalid .value {
  text-decoration: line-through;
  color: #94a3b8;
}

.badge-info.invalid .badge-title,
.badge-info.invalid .badge-type,
.badge-info.invalid h3 {
  color: #94a3b8;
}

.badge-info.invalid .badge-image {
  background: linear-gradient(135deg, #94a3b8, #cbd5e1);
  box-shadow: none;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #e5e7eb;
  color: #374151;
}

.modal-content h2 {
  margin: 0;
  padding: 24px 60px 16px 24px;
  font-size: 1.5rem;
  color: #111827;
  border-bottom: 1px solid #e5e7eb;
}

.about-content {
  padding: 24px;
}

.about-content section {
  margin-bottom: 24px;
}

.about-content section:last-child {
  margin-bottom: 0;
}

.about-content h3 {
  margin: 0 0 12px;
  font-size: 1.1rem;
  color: #1f2937;
}

.about-content p {
  margin: 0 0 12px;
  color: #4b5563;
  line-height: 1.6;
}

.about-content ul {
  margin: 0;
  padding-left: 20px;
  list-style: disc;
}

.about-content li {
  color: #4b5563;
  margin-bottom: 8px;
  line-height: 1.5;
}

.about-content li:last-child {
  margin-bottom: 0;
}

.about-content code {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
  color: #ef4444;
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95) translateY(-20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-container {
    max-width: 95%;
    padding: 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }

  .badge-layout {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .badge-left-column {
    align-items: center;
  }

  .badge-image {
    width: 150px;
    height: 150px;
  }

  .badge-emoji {
    font-size: 4rem;
  }

  .badge-title {
    font-size: 2rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .label {
    text-align: left;
  }

  .value {
    text-align: left;
    margin-top: 0.25rem;
  }
}
</style>