"use strict";
/* WebSockets */
function sendJSON(socket, obj) {
  socket.send(JSON.stringify(obj));
}

function make_connection (name) {
  var socket = new WebSocket('ws://' + location.hostname + ':8080/ws');
  socket.onopen = function() {
    socket.send(name)
  }

  socket.onclose = function() {
    alert("Server closed connection")
  }

  socket.onmessage = function(evt) {
    var message = JSON.parse(evt.data)
    socket.dispatchEvent(new CustomEvent(message.type, {'detail': message}))
  }
  return socket;
}

/* Setup Chart.js */
Chart.defaults.global.legend.position = "right";
Chart.defaults.global.elements.line.fill = false;
Chart.defaults.line.scales.xAxes = [{
  type: 'time',
  time: {
    unit: 'week',
  },
}];

/* Setup Vue */
function define_components(connection) {
  /* Vue filters */
  Vue.filter('round', function(value) {
    value = parseFloat(value);
    value = Math.round((value + 0.0001) * 100) / 100;
    value = value.toString()
    var x = value.split('.');
    var x1 = x[0];
    var x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
      x1 = x1.replace(rgx, '$1' + ' ' + '$2');
    }
    return x1 + x2;
  })

  /* Vue components */
  Vue.component('etg-monitor', {
    template: '<div class="monitor"><h4><slot>{{ monitor }}</slot></h4><span>{{ value | round }}</span></div>',
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
    },
    created: function() {
      var mon = this
      connection.addEventListener('change', function(e) {
        var data = e.detail.packet;
        if (data[mon.monitor]) {
          mon.value = data[mon.monitor]
        }
      })
    }
  })

  Vue.component('etg-slider', {
    template: `
    <div class="slider">
    <h4><slot>{{ ident }}</slot></h4>
    <div class="rowcontainer">
    <input v-model.number="value" type="range"
    :min="min" :max="max" :step="step"
    v-on:input="update($event.target.value)">
    </input>
    <span>{{ value | round }} {{ unit }}</span>
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
    methods: {
      update: function(value) {
        this.value = parseFloat(value);
        sendJSON(socket, {'type': 'change',
                           'packet': {[this.ident]: this.value}});
      },
    },
    created: function() {
      var mon = this
      connection.addEventListener('change', function(e) {
        data = e.detail.packet;
        if (data[mon.ident]) {
          mon.value = data[mon.ident]
        }
      })
    }
  })

  Vue.component('etg-plot-container', {
    created: function() {
      this.plots = {};
      this.titles = [];
      if (this.$slots.default) {
        console.log(this.$slots.default);
        for (let node of this.$slots.default) {
          console.log(node)
          var title = node.componentOptions.propsData.title;
          this.plots[title] = node;
          this.titles.push(title);
        }
        this.title = this.titles[0];
        console.log(this.plots)
      }
    },
    render: function(createElement) {
      console.log("Rendering")
      console.log(this.title)
      if (this.titles.length === 0){
        return create('span', 'No plots to display');
      } else if (this.titles.length === 1) {
        return this.plots[this.titles[0]];
      }
      var self = this;
      var select = createElement('select', {
        domProps: {
          value: self.title
        },
        on: {
          change: function (event) {
            self.title = event.target.value
            self.$emit('change', event.target.value)
            self.$forceUpdate()
            console.log("New title: " + self.title)
          }
        }
      },
        this.titles.map(t => createElement('option', t)));
      console.log(this.title)
      console.log(this.plots[this.title])
      return createElement('div', [this.plots[this.title], select]);
    }
  });

  Vue.component('etg-plot', {
    template: '<canvas class="plot"></canvas>',
    props: {
      variable: {
        type: String,
        required: true,
      },
      collection: {
        type: String,
        required: true,
      },
      overlay: {
        type: String,
        required: false,
      },
      title: {
        type: String,
        required: false,
        default: '',
      },
      min: {
        type: Number,
        required: false,
        default: 0
      },
      max: {
        type: Number,
        required: false,
      },
      maxdata: {
        type: Number,
        required: false,
        default: 10
      },
    },

    mounted: function() {
      var coll = this.$root[this.collection];
      var length = coll.length;
      var data = {
        labels: [this.$root.current_date],
        datasets: []
      };
      var coll = this.$root[this.collection];
      var length = coll.length;
      // Building the datasets
      for (var i = 0; i < length; i++) {
        data.datasets.push({
          label: coll[i].name,
          data: [coll[i][this.variable]],
          borderColor: 'rgb(0,0,255)',
        });
      }
      if (this.overlay) {
        data.datasets.push({
          label: this.overlay,
          data: [this.$root[this.overlay]],
          borderColor: 'rgb(0,0,0)',
        })
      }
      console.log(data)
      var ctx = this.$el.getContext('2d');
      var title = {display: false}
      if (this.title) {
        title.display = true;
        title.text = this.title;
      }
      var ticks = {suggestedMin: this.min};
      if (this.max !== undefined) {
        ticks.suggestedMax = this.max;
      }
      this.chart = new Chart(ctx, {
        type: "line",
        data: data,
        options: {
          title: title,
          scales: {
            yAxes: [{
              ticks: ticks,
            }],
          },
        },
      });
      // Register for events
      var self = this;
      connection.addEventListener('change', function(e) {
        var data = e.detail.packet;
        console.log(data);
        if (data[self.collection]) {
          var coll = data[self.collection];
          if (coll[0][self.variable] !== undefined) {
            var pop_data = false;
            if (self.chart.data.labels.length >= self.maxdata) {
              self.chart.data.labels.shift()
              pop_data = true;
            }
            self.chart.data.labels.push(data.current_date);
            self.chart.data.datasets.forEach((dataset) => {
              if (pop_data) {
                dataset.data.shift()
              }
              var value = undefined;
              if (dataset.label === self.overlay) {
                value = self.$root[self.overlay];
              } else {
                value = coll.filter((val) => val.name === dataset.label)[0];
                value = value[self.variable];
              }
              dataset.data.push(value);
            });
            self.chart.update()
          }
        }
      });
    },
  })
}

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

function setup_vue(data, socket) {
  window.vm = new Vue({
    el: "#content",
    delimiters: ['[[', ']]'],
    data: data,
    methods: {
      changeTax: function(energy_type, amount) {
        var data = this.taxes;
        data[energy_type] += amount;
        sendJSON(socket, {'type': 'change', 'packet': {'taxes': data}})
      },
      updateMarket: function(name, value) {
        if (value < 0) {
          value = 0;
          vm.market[name] = 0;
        }
        socket.send(JSON.stringify({'type': 'change', 'packet':
          {'market': {name: value}}}))
      }
    },
    filters: {
      capitalize: function (value) {
        if (!value) return ''
        value = value.toString()
        return value.charAt(0).toUpperCase() + value.slice(1)
      },
    }
  })
  socket.dispatchEvent(new CustomEvent('change', {'detail': {'packet': data}}))
}
