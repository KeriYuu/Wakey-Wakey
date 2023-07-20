<template>
  <div class="rawText">
    <input 
    type="text" 
    :value="msg"
    @change="textChange"
    >
	<canvas id="wordcanvas"></canvas>
  </div>
</template>

<script>

export default {
  name: 'DisplayText',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
</style>
