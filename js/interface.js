/* Vue components */
Vue.component('etg-monitor', {
  template: '<div class="monitor"><h4><slot>{{ monitor }}</slot></h4><span>{{ value }}</span></div>',
  props: {
    monitor: {
      type: String,
      required: true
    }
  },
  data: function() {
    return {
      value: 0
    }
  }
})

Vue.component('etg-slider', {
  template: `
  <div class="slider">
    <h4><slot>{{ ident }}</slot></h4>
    <div class="rowcontainer">
      <input v-model="value" type="range"
          :min="min" :max="max" :step="step">
      </input>
      <span>{{ value }} {{ unit }}</span>
    </div>
  </div>`,
  props: {
    ident: {
      type: String,
      required: true
    },
    init: {
      type: Number,
      required: false,
      default: 0
    },
    unit: {
      type: String,
      default: '%'
    },
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      default: 100
    },
    step: {
      type: Number,
      default: 1
    },
  },
  data: function() {
    return {
      value: this.init
    }
  },
})

Vue.component('plot', {
  template: '<div class = "plot"></div>',
})

/* Tab functionality */
function openTab(event, name) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }

  // Show the current tab, and add an "active" class to the link that opened the tab
  document.getElementById(name).style.display = "block";
  event.currentTarget.className += " active";
}

/* Setting up everything */
window.onload = function() {
  window.vm = new Vue({
    el: '#content',
    delimiters: ['[[', ']]'],
    data: {
      date: 'Today',
      weather: 'Quite Sunny',
      ruling_party: 'The Green Party',
      donate_party: 'The Green Party',
      donate_amount: 10000,
      newsfeed: [
        'Nuclear reactor exploded',
        'More bullshit news',
        'Clown elected president on Mars',
        'djkajflkdasfdalkjfdkl',
        'A puppy got lost',
        'We have no more icecream',
        'The moon exploded',
        'The summer is actually not coming',
      ],
      solar: {
        price_bruto: 0,
        price_average: 0,
        tax: 0,
        level: 0,
        upgrade_price: 10000,
        sell_price: 5000,
      },
      wind: {
        price_bruto: 0,
        price_average: 0,
        tax: 0,
        upgrade_price: 10000,
        sell_price: 5000,
      },
      nuclear: {
        price_bruto: 0,
        price_average: 0,
        tax: 0,
        upgrade_price: 10000,
        sell_price: 5000,
      },
      oil: {
        price_bruto: 0,
        price_average: 0,
        tax: 0,
        upgrade_price: 10000,
        sell_price: 5000,
      },
      gas: {
        price_bruto: 0,
        price_average: 0,
        tax: 0,
        upgrade_price: 10000,
        sell_price: 5000,
      },
      coal: {
        price_bruto: 0,
        price_average: 0,
        tax: 0,
        upgrade_price: 10000,
        sell_price: 5000,
      },
    }
  })
  openTab({currentTarget: document.getElementById('button-Inputs')}, 'Inputs');
}
