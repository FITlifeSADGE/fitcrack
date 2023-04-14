<!--
   * Author : see AUTHORS
   * Licence: MIT, see LICENSE
-->

<template>
  <v-data-table v-model="selected" :headers="headers" :items="rainbowTables.items" :items-per-page="itemsPerPage"
    :footer-props="footerProps" :search="search" item-key="id" show-select :single-select="!selectAll"
    @input="updateSelected">
    <template v-slot:item.name="{ item }">
      <router-link :to="{name: 'rainbowTablesDetail', params: { id: item.id}}">
        {{ item.name }}
      </router-link>
    </template>
    <template v-slot:item.actions="{ item }">
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <a :href="$serverAddr + '/rainbowTables/download/' + item.name" target="_blank" download v-on="on">
            <v-btn icon>
              <v-icon>mdi-file-download-outline</v-icon>
            </v-btn>
          </a>
        </template>
        <span>Download</span>
      </v-tooltip>
    </template>
  </v-data-table>
</template>
  
<script>
import fmt from '@/assets/scripts/numberFormat'
import selector from './selectorMixin'
export default {
  name: "RainbowSelector",
  mixins: [selector],
  data() {
    return {
      headers: [
        { text: 'Name', align: 'start', value: 'name' },
        { text: 'Charset range', value: 'range', align: 'end' },
        { text: 'Hash algorithm', value: 'algorithm', align: 'end' },
        { text: 'Success rate', value: 'number', align: 'end' },
        { text: 'Actions', value: 'actions', align: 'end', sortable: false }
      ],
      rainbowTables: []
    }
  },
  methods: {
    fmt,
    getData: function () {
      this.loading = true;
      console.log(this.$serverAddr + '/rainbowTables/loadall')
      this.axios.get(this.$serverAddr + '/rainbowTables/loadall').then((response) => {
        this.rainbowTables = response.data;
        this.loading = false
      })
    }
  }
}
</script>
  