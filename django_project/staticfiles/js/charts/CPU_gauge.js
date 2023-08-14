function createChartDiv(id, width, height) {
  const chartDiv = document.createElement("div");
  chartDiv.setAttribute("id", id);
  chartDiv.style.width = width;
  chartDiv.style.height = height;
  return chartDiv;
}

function initChart(chartDom) {
  const myChart = echarts.init(chartDom);

  const option = {
    series: [
      {
        type: "gauge",
        min: 0,
        max: 100,
        splitNumber: 4,
        axisLine: {
          lineStyle: {
            width: 30,
            color: [
              [0.3, "#67e0e3"],
              [0.7, "#37a2da"],
              [1, "#fd666d"],
            ],
          },
        },
        axisTick: {
          distance: -30,
          length: 8,
          lineStyle: {
            color: "#fff",
            width: 2,
          },
        },
        splitLine: {
          distance: -30,
          length: 30,
          lineStyle: {
            color: "#fff",
            width: 4,
          },
        },
        axisLabel: {
          color: "inherit",
          distance: 40,
          fontSize: 20,
          formatter: "{value}%",
        },
        detail: {
          valueAnimation: true,
          formatter: "{value}%",
          color: "inherit",
        },
        data: [
          {
            value: 50,
          },
        ],
      },
    ],
  };

  myChart.setOption(option);
}

const chartDiv = createChartDiv("hello", "600px", "400px");
const parentElement = document.querySelector(".system-metrics");
parentElement.appendChild(chartDiv);

const chartDom = document.getElementById("hello");
initChart(chartDom);
