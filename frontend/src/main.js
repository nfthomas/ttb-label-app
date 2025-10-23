import { createApp } from 'vue'
import App from './App.vue'
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';

import 'primevue/resources/themes/aura-light-blue/theme.css';
import './assets/main.css';

import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import FileUpload from 'primevue/fileupload';
import Button from 'primevue/button';
import Toast from 'primevue/toast';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';

const app = createApp(App);

app.use(PrimeVue, { ripple: true });
app.use(ToastService);

app.component('Card', Card);
app.component('InputText', InputText);
app.component('InputNumber', InputNumber);
app.component('FileUpload', FileUpload);
app.component('Button', Button);
app.component('Toast', Toast);
app.component('Accordion', Accordion);
app.component('AccordionTab', AccordionTab);

app.mount('#app');