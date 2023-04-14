<template>
  <div>
    <v-card-title>
      <span>Select rainbow table<span class="required primary--text"> *</span></span>
    </v-card-title>
    <rainbow-selector v-model="rainbows" select-all @input="checkValid" />
  </div>
</template>
  

<script>
import RainbowSelector from '@/components/selector/rainbowSelector.vue'

import { mapTwoWayState } from 'spyfu-vuex-helpers'
import { twoWayMap } from '@/store'

export default {
  name: "Rainbow",
  components: {
    'rainbow-selector': RainbowSelector
  },
  computed: mapTwoWayState('jobForm', twoWayMap(['rainbows'])),
  methods: {
    checkValid: function () {
      return true
    }
  }
}
</script>

<style scoped>
.required {
  font-weight: bold;
  color: #000;
}
</style>