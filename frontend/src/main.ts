import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

const themeKey = 'bilibili-monitor-theme'
const savedTheme = localStorage.getItem(themeKey)
const initialTheme = savedTheme === 'dark' ? 'dark' : 'light'
document.body.dataset.theme = initialTheme

const themeButton = document.createElement('button')
themeButton.className = 'theme-toggle icon-button'
themeButton.type = 'button'
themeButton.title = initialTheme === 'dark' ? '切换浅色主题' : '切换深色主题'
themeButton.setAttribute('aria-label', themeButton.title)
document.body.appendChild(themeButton)

function renderThemeButton(theme: 'light' | 'dark') {
  themeButton.textContent = theme === 'dark' ? '☀' : '☾'
  themeButton.title = theme === 'dark' ? '切换浅色主题' : '切换深色主题'
  themeButton.setAttribute('aria-label', themeButton.title)
}
renderThemeButton(initialTheme)
themeButton.addEventListener('click', () => {
  const theme = document.body.dataset.theme === 'dark' ? 'light' : 'dark'
  document.body.dataset.theme = theme
  localStorage.setItem(themeKey, theme)
  renderThemeButton(theme)
})

createApp(App).mount('#app')
