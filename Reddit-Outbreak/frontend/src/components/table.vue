<template>
<div id="table">
  <ul v-for="item in summary" :key="item.state.In">
    <li class="outbreak collection">
      <div class="name">
        <span class="">{{item.subreddit}}</span>
      </div>
      <div class="button" @click="$emit('click',item.subreddit)">
        <a class="waves-effect waves-light btn red lighten-2">
          <i class="material-icons left">visibility</i>
          view
        </a>
      </div>
    </li>
  </ul>
</div>
</template>

<script>
export default {
  name: 'componentTable',
  props: ['summary'],
};
</script>

<style scoped lang="scss">
.outbreak{
  height: 50px;
  display: flex;
  flex-direction: row;
  margin:0;

  div.name {
    width: 60%;
    display: flex;
    justify-content: center;
    align-content: center;

    span{
      margin:auto;
      margin-left: 10%;
      font-size: 1.35em;
      font-family: 'EB Garamond', serif;
      padding-right: 5px;
      overflow-x: hidden;
    }
  }
  div.button{
    width: 40%;
    border-left: 1px gray dashed;
    padding-left: 10px;
    a {
      max-width: 120px;
      width:85%;
      padding-left: 10px;
      padding-right: 10px;
      margin-top: 6px;
      font-size: 95%;
    }
  }
}

ul {
  margin:5px;
}
</style>
