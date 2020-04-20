<template>
  <div id="wrapper">
    <div id="header">
      <h3 class="">Covid-Reddit</h3>
    </div>
    <div id="content">
      <div id="table" class="card">
        <h5>Worst Outbreaks</h5>
        <componentTable :summary='summary' @click='handleClick'></componentTable>
      </div>
      <div id="plot" class="card">
        <componentPlot :selectedData='selectedData'> </componentPlot>
      </div>
    </div>
  </div>
</template>
<script>
import componentTable from './table.vue';
import componentPlot from './plot.vue';

// Define some constants
const URL = 'https://leviborodenko.github.io/data-playground/db.json';

// helping methods
// function that grabs our infection data
async function getData() {
  const response = await fetch(URL, { cache: 'no-cache' });

  if (!response.ok) {
    M.toast({html: `No outbreaks yet!`, displayLength: 5000});
    return null;
  } else {
    const data = await response.json();
    return data;
  }

}

function getOutbreakSummary(data) {
  const outbreakLocations = Object.keys(data);

  const summary = outbreakLocations.map((value) => ({
    subreddit: value,
    state: data[value].state,
  }));

  return summary;
}

function timeout(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function handleClick(event) {
  const { state } = this.state[event];
  const percentInfected = state.In / (state.In + state.R + state.D + state.S);
  let usePercentage = false;
  if (percentInfected > 0.01) {
    usePercentage = true;
  }

  const selectedData = {
    name: event,
    data: this.state[event].data,
    usePercent: usePercentage,
  };

  this.selectedData = selectedData;
  M.toast({html: `Viewing /r/${event}`, displayLength: 1000});
}

export default {
  name: 'ComponentMain',
  components: {
    componentPlot,
    componentTable,
  },

  data: () => ({
    state: null,
    summary: null,
    selectedData: null,
  }),

  async mounted() {
    while (true) {
      this.state = await getData();

      if(this.state == null) {
        
        await timeout(10 * 1000);
        M.toast({html: `Reloading.`, displayLength: 2000});
        await timeout(2 * 1000);
      
      } else {
        this.summary = getOutbreakSummary(this.state);
        
        if (this.selectedData != null) {
          handleClick.bind(this)(this.selectedData.name);
        }

        await timeout(120 * 1000);
        M.toast({html: `Reloading.`, displayLength: 2000});
      }


      
    }
  },

  methods: {
    handleClick,
  },
};

</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
// CSS FOR LARGE SCREENs
div#wrapper {
  width: 95vw;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-content: center;
  margin-left: 2.5vw;

  div#header {
    grid-area: header;
    display: flex;
    flex-direction: row;
    align-self: center;
    white-space: nowrap;
    height: max(10vh, 50px);

    h3 {
      font-family: 'EB Garamond', serif;
      color: #444;
      margin: auto;
    }
  }

  div#content {
    display: flex;
    flex-direction: row;
    justify-content: center;

    div#table {
      width: min(30vw, 400px);
      margin-right: 2.5vw;
      overflow-y: scroll;
      overflow-x: hidden;
      max-height: min(60vw, 500px);
    }

    div#plot {
      width: min(60vw, 500px);
      height: min(60vw, 500px);
    }
  }
}

// CSS for mobile
@media screen and (max-width: 560px) {
  div#wrapper {
    width: 95vw;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-content: center;
    margin-left: 2.5vw;

    div#header {
      grid-area: header;
      display: flex;
      flex-direction: row;
      align-self: center;
      white-space: nowrap;
      height: 50px;

      h3 {
        font-family: 'EB Garamond', serif;
        color: #444;
        margin: auto;
      }
    }

    div#content {
      display: flex;
      flex-direction: column;
      min-height: 50vh;
      align-content: center;


      div#table {
        width: 80vw;
        margin: auto;
        margin-bottom: 15px;
        margin-top: 15px;
        height: 43vh;
        min-height: 150px;

      }

      div#plot {
        width: 80vw;
        height: 80vw;
        margin: auto;
      }
    }
  }
}

// For all sizes
div#table {
  display: flex;
  flex-direction: column;
  align-content: center;

  h5 {
    text-align: center;
    margin-left: 20%;
    margin-right: 20%;
    color: #444;
    padding-bottom: 5px;
    border-bottom: 1px lighten(#444, 20%) dashed;
    font-family: 'EB Garamond', serif;
  }
}

</style>
