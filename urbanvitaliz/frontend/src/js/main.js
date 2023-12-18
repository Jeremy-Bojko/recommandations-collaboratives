import 'vite/modulepreload-polyfill';
import './utils/globals'

//Global Store
import './store/utils'
import './store/editor'
import './store/djangoData'
import './store/app'

//Global reused component
import './components/Notification'
import './components/Editor'

//Global CSS
import '../css/buttons.css'
import '../css/input.css'
import '../css/typography.css'
import '../css/hover.css'
import '../css/colors.css'
import '../css/text-colors.css'
import '../css/border.css'
import '../css/role.css'

//Layouts CSS
import '../css/stack.css'

//Global reused component CSS
import '../css/flags.css'
import '../css/user.css'
import '../css/callout.css'
import '../css/markdown.css'
import '../css/miscellaneous.css'

console.log('js main added');
