import{_ as e,j as t,e as a,y as i,J as d,d as o,n as s}from"./main-22e4648c.js";import"./c.fed73dd4.js";import"./c.2c462191.js";import"./c.8e1ed6df.js";import"./c.8e28b461.js";import"./c.fa63af8a.js";import"./c.19945fa6.js";let l=e([s("ha-selector-template")],(function(e,t){return{F:class extends t{constructor(...t){super(...t),e(this)}},d:[{kind:"field",decorators:[a()],key:"hass",value:void 0},{kind:"field",decorators:[a()],key:"value",value:void 0},{kind:"field",decorators:[a()],key:"label",value:void 0},{kind:"field",decorators:[a()],key:"helper",value:void 0},{kind:"field",decorators:[a({type:Boolean})],key:"disabled",value:()=>!1},{kind:"field",decorators:[a({type:Boolean})],key:"required",value:()=>!0},{kind:"method",key:"render",value:function(){return i`
      ${this.label?i`<p>${this.label}${this.required?" *":""}</p>`:""}
      <ha-code-editor
        mode="jinja2"
        .hass=${this.hass}
        .value=${this.value}
        .readOnly=${this.disabled}
        autofocus
        autocomplete-entities
        autocomplete-icons
        @value-changed=${this._handleChange}
        dir="ltr"
      ></ha-code-editor>
      ${this.helper?i`<ha-input-helper-text>${this.helper}</ha-input-helper-text>`:""}
    `}},{kind:"method",key:"_handleChange",value:function(e){const t=e.target.value;this.value!==t&&d(this,"value-changed",{value:t})}},{kind:"get",static:!0,key:"styles",value:function(){return o`
      p {
        margin-top: 0;
      }
    `}}]}}),t);export{l as HaTemplateSelector};