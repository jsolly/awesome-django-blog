// my_chart.js

// Get the DOM element where the chart will be rendered
var chartDom = document.getElementById('hello');
// Initialize the chart using the echarts library
var myChart = echarts.init(chartDom);
// Define the chart options
var option;

option = {
  series: [
    {
      type: 'gauge',
      min: 0, // Set the minimum value of the gauge
      max: 100, // Set the maximum value of the gauge
      splitNumber: 4, // Set the number of split segments
      axisLine: {
        lineStyle: {
          width: 30,
          color: [
            [0.3, '#67e0e3'],
            [0.7, '#37a2da'],
            [1, '#fd666d']
          ]
        }
      },
      pointer: {
        itemStyle: {
          color: 'inherit'
        }
      },
      axisTick: {
        distance: -30,
        length: 8,
        lineStyle: {
          color: '#fff',
          width: 2
        }
      },
      splitLine: {
        distance: -30,
        length: 30,
        lineStyle: {
          color: '#fff',
          width: 4
        }
      },
      axisLabel: {
        color: 'inherit',
        distance: 40,
        fontSize: 20,
        formatter: '{value}%' // Change the formatter to display a percentage
      },
      detail: {
        valueAnimation: true,
        formatter: '{value}%', // Change the formatter to display a percentage
        color: 'inherit'
      },
      data: [
        {
          value: 70
        }
      ]
    }
  ]
};
// Set the chart options
option && myChart.setOption(option);

// Update the chart data at regular intervals
setInterval(function () {
  myChart.setOption({
    series: [
      {
        data: [
          {
            value: +(Math.random() * 100).toFixed(2)
          }
        ]
      }
    ]
  });
}, 2000);
