<template>
  <div id="plot">
    <div class="placeholder">Please Select An Outbreak</div>
  </div>
</template>
<script>
import * as c3 from 'c3';

// Helper functions
function percentTick(text) {
  if (text > 100) {
    return '';
  }
  return `${text}%`;
}

function round(num) {
  return Number.parseFloat(num).toPrecision(3);
}

function normaliseRecord(record) {
  const norm = (record.D + record.In + record.R + record.S) / 100;
  return {
    D: round(record.D / norm),
    In: round(record.In / norm),
    R: round(record.R / norm),
    Time: record.Time,
  };
}

// handling data
function toPercentData(data) {
  return data.map(normaliseRecord);
}

function handleSelectedDataChange(selectedData) {
  if (selectedData == null) {
    return false;
  }
  let { data } = selectedData;
  const { usePercent } = selectedData;

  let tickFunc = (text) => text;
  if (usePercent) {
    data = toPercentData(data);
    tickFunc = percentTick;
  }

  c3.generate({
    bindto: '#plot',
    data: {
      json: data,
      keys: {
        x: 'Time',
        value: ['In', 'D', 'R'],
      },
      names: {
        In: 'Infected',
        D: 'Dead',
        R: 'Recovered',
      },
      colors: {
        In: '#d62728',
        D: 'black',
        Recovered: '#2ca02c',
      },
      type: 'bar',
      groups: [
        ['In', 'D', 'R'],
      ],
    },
    axis: {
      x: {
        type: 'timeseries',
      },
      y: {
        tick: {
          format: tickFunc,
        },
      },
      labels: {
        x: 'Time',
        y: 'Percentage',
      },
    },
    padding: {
      right: 5,
      top: 5,
    },
  });

  return true;
}

export default {
  name: 'componentPlot',
  props: ['selectedData'],
  watch: {
    selectedData: handleSelectedDataChange,
  },
};

</script>
<style scoped lang="scss">
#plot {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-content: center;

  .placeholder {
    text-align: center;
    align-self: center;
    color: gray;
    font-family: 'Quicksand';
    font-size: 2em;
  }
}

</style>
