<!--
   * Author : see AUTHORS
   * Licence: MIT, see LICENSE
-->

<template>
  <v-container class="rmw mt-4">
    <v-row>
      <v-col>
        <fc-tile title="Rainbow Tables" class="ma-2">
          <v-alert tile text type="warning" class="mb-0">
            Rainbow Tables use .csv extension.
          </v-alert>
          <v-expansion-panels flat class="mt-6">
            <v-expansion-panel>
              <v-expansion-panel-header class="px-4">
                <template v-slot:default="{ open }">
                  <span class="d-flex align-center">
                    <span class="text-h6">{{ open ? '' : 'Show ' }}Rainbow Table generating</span>
                  </span>
                </template>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-card-text>
                  <v-text-field :loading="loading" outlined type="number" label="Min plaintext len" min="1" max="30"
                    hint="Select the minimum length of plaintexts" persistent-hint suffix="characters" class="mb-4"
                    value="5" v-model="MinPlaintextLen" />

                  <v-text-field :loading="loading" outlined type="number" label="Max plaintext len" min="1" max="30"
                    hint="Select the maximum length of plaintexts" persistent-hint suffix="characters" class="mb-4"
                    value="10" v-model="MaxPlaintextLen" />

                  <v-text-field :loading="loading" outlined type="number" label="Number of rows" min="1"
                    hint="Select the number of rows" persistent-hint suffix="rows" class="mb-4" value="1000"
                    v-model="RowCount" />

                  <v-text-field :loading="loading" outlined type="number" label="Number of columns" min="1"
                    hint="Select the number of columns" persistent-hint suffix="columns" class="mb-4" value="1000"
                    v-model="ColumnCount" />

                  <v-autocomplete id="hash-type-select" v-model="hashType" editable validate-on-blur clearable
                    label="Select hash type" :items="hashTypes" item-text="name" :filter="hashTypeFilter" return-object
                    required hide-details single-line flat solo-inverted no-data-text="No matching hash type">
                    <template #item="{ item }">
                      <v-list-item-content>
                        <v-list-item-title><b>{{ item.code }}</b> - {{ item.name }}</v-list-item-title>
                      </v-list-item-content>
                    </template>
                  </v-autocomplete>

                  <v-autocomplete id="charset-type-select" editable validate-on-blur clearable label="Select charset"
                    :items="charsetTypes" item-text="name" return-object required hide-details single-line flat
                    solo-inverted no-data-text="No matching charset" v-model="charsetType">
                    <template #item="{ item }">
                      <v-list-item-content>
                        <v-list-item-title><b>{{ item.name }}</b></v-list-item-title>
                      </v-list-item-content>
                    </template>
                  </v-autocomplete>
                  <v-dialog v-model="dialog" class="text-right pa-3">
                    <template v-slot:activator="{ on }">
                      <v-btn v-on="on" class="d-inline-block" color="primary" outlined>
                        Display characters
                      </v-btn>
                    </template>
                    <v-card>
                      <v-card-text>
                        <ul>
                          <li v-for="(item, index) in this.charsetTypes" :key="index" style="font-size: 15px;">
                            <b>{{ item.name }}</b> : {{ item.characters }}
                          </li>
                        </ul>
                      </v-card-text>
                    </v-card>
                  </v-dialog>
                  <v-dialog v-model="generating" class="text-right pa-3">
                    <template v-slot:activator="{ on }">
                      <v-btn v-on="on" class="d-inline-block" color="primary" outlined
                        @click="getEstimate(ColumnCount, RowCount, hashType, charsetType, MaxPlaintextLen)">
                        Generate
                      </v-btn>
                    </template>
                    <v-card>
                      <v-card-text v-if="hash_input">
                        <b style="font-size: 15px; margin-bottom: 20px;">{{ message }}</b>
                        <div>
                          <v-text-field v-model="filename" outlined autofocus required label="Filename"
                            hint="Give this rainbow table a descriptive name" persistent-hint />
                          <v-btn class="d-inline-block" color="primary" text outlined :disabled="!filename"
                            @click="genRainbowTable(MinPlaintextLen, MaxPlaintextLen, charsetType, hashType, ColumnCount, RowCount, filename)">
                            Confirm and generate
                          </v-btn>
                          <a :href="downloadTable" target="_blank" download>
                            <v-btn class="d-inline-block" color="primary" text outlined :disabled="!generated">
                              Download
                            </v-btn>
                          </a>
                          <div v-if="loading" style="text-align: center;">
                              Generating table in progress...
                            <v-progress-linear indeterminate color="primary" class="mt-3"></v-progress-linear>
                          </div>
                        </div>
                      </v-card-text>
                      <v-card-text v-else>
                        Some fields appear to be empty or invalid. Please check your input.
                      </v-card-text>
                    </v-card>
                  </v-dialog>
                </v-card-text>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <v-expansion-panels flat class="mt-7">
            <v-expansion-panel>
              <v-expansion-panel-header class="px-4">
                <template v-slot:default="{ open }">
                  <span class="d-flex align-center">
                    <span class="text-h6">{{ open ? '' : 'Browse ' }}Rainbow Tables</span>
                  </span>
                </template>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-card-text>
                  <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line
                    hide-details></v-text-field>
                  <v-data-table :headers="headers" :items="rainbowTables.items" :loading="loading" :search="search"
                    :footer-props="{ itemsPerPageOptions: [10, 25, 50], itemsPerPageText: 'Rainbow tables per page' }">
                    <template v-slot:item.name="{ item }">
                      <router-link :to="`rainbowTables/${item.id}`">
                        {{ item.name }}
                      </router-link>
                    </template>
                    <template v-slot:item.number="{ item }">
                      {{ item.number }}%
                    </template>
                    <template v-slot:item.actions="{ item }">
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <a :href="$serverAddr + '/rainbowTables/download/' + item.name" target="_blank" download
                            v-on="on">
                            <v-btn icon>
                              <v-icon>mdi-file-download-outline</v-icon>
                            </v-btn>
                          </a>
                        </template>
                        <span>Download</span>
                      </v-tooltip>
                    </template>
                  </v-data-table>
                  <file-uploader :url="this.$serverAddr + '/rainbowTables/add'" @uploadComplete="loadAllRainbowTables" />
                </v-card-text>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <v-expansion-panels flat class="mt-8">
            <v-expansion-panel>
              <v-expansion-panel-header class="px-4">
                <template v-slot:default="{ open }">
                  <span class="d-flex align-center">
                    <span class="text-h6">{{ open ? '' : '' }}Crack hashes using Rainbow Tables</span>
                  </span>
                </template>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-card-text>
                  <v-stepper id="job-stepper" v-model="step" vertical non-linear class="mb-4">
                    <v-stepper-step id="job-step-1" editable step="1">
                      Enter hashes
                    </v-stepper-step>
                    <v-stepper-content step="1">
                      <v-autocomplete id="hash-type-select" v-model="hashType" editable validate-on-blur clearable
                        label="Select hash type" :items="hashTypes" item-text="name" :filter="hashTypeFilter"
                        return-object required hide-details single-line flat solo-inverted
                        no-data-text="No matching hash type" @change="validateHashes(null)">
                        <template #item="{ item }">
                          <v-list-item-content>
                            <v-list-item-title><b>{{ item.code }}</b> - {{ item.name }}</v-list-item-title>
                          </v-list-item-content>
                        </template>
                      </v-autocomplete>

                      <fc-textarea id="hashes-input" v-if="inputMethod !== null" ref="textarea" v-model="hashList"
                        :class="{ 'hasherror': hashListError }" class="textarea" max-height="500"
                        :readonly="!(inputMethod === 'multipleHashes' && !gotBinaryHash)" :can-remove-line="true"
                        @blur="validateHashes" @focus="unvalidateHashes">
                        <div slot="after" class="hashCeckContainer pl-1 pt-2">
                          <div v-for="hashObj in validatedHashes" :key="hashObj.id">
                            <v-icon v-if="hashObj.result === 'OK'" small color="success">
                              check_circle_outlined
                            </v-icon>
                            <v-tooltip v-else left>
                              <template v-slot:activator="{ on }">
                                <v-icon small color="error" class="clickable" v-on="on">
                                  error_circle_outlined
                                </v-icon>
                              </template>
                              <span>{{ hashObj.result }}</span>
                            </v-tooltip>
                            <v-tooltip v-if="hashObj.isInCache" left>
                              <template v-slot:activator="{ on }">
                                <v-icon small color="warning" class="clickable" v-on="on">
                                  error_circle_outlined
                                </v-icon>
                              </template>
                              <span>hash already in hashcache</span>
                              <br>
                              <span> password: {{ hashObj.password }} </span>
                            </v-tooltip>
                          </div>
                        </div>
                      </fc-textarea>
                      <v-btn color="primary" @click="step = 2">
                        Next
                      </v-btn>
                    </v-stepper-content>
                    <v-stepper-step id="job-step-2" editable step="2">
                      Select rainbow table
                    </v-stepper-step>
                    <v-stepper-content step="2">
                      <v-container>
                        <div>
                          <v-card-title>
                            <span>Select rainbow table<span class="required primary--text"> *</span></span>
                          </v-card-title>
                          <rainbow-selector v-model="rainbows" select-all />
                        </div>

                        <v-row>
                          <v-spacer />
                          <v-btn class="mr-6 mt-4" color="primary" @click="step = 3">
                            Next
                          </v-btn>
                        </v-row>
                      </v-container>
                    </v-stepper-content>
                    <v-stepper-step id="job-step-3" editable step="3">
                      Crack hashes
                    </v-stepper-step>
                    <v-stepper-content step="3">
                      <v-container>
                        <div>
                          <v-card-title>
                            <span>Entered hashes</span>
                          </v-card-title>
                          <div :key="hashObj.id" v-for="hashObj in validatedHashes">
                            <v-card-text>
                              <span>{{ hashObj.hash }}
                                <div v-for="(value, key) in getPasswords.items" :key="key" v-if="key === hashObj.hash"> password: <b>{{
                                  value }}</b></div>
                              </span>
                            </v-card-text>
                          </div>
                        </div>

                        <v-row>
                          <v-spacer />
                          <v-btn class="mr-6 mt-4" color="primary" @click="CrackEnteredHashes(hashList, rainbows)">
                            Crack hashes
                          </v-btn>
                        </v-row>
                        <div v-if="loading">
                          Cracking hashes in progress...
                          <v-progress-linear indeterminate color="primary" class="mt-3"></v-progress-linear>
                        </div>
                      </v-container>
                    </v-stepper-content>
                  </v-stepper>
                </v-card-text>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </fc-tile>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import FileUploader from "@/components/fileUploader/fileUploader.vue";
import fcTextarea from '@/components/textarea/fc_textarea.vue'
import templateModal from '@/components/jobTemplate/templateModal.vue'
import { mapState, mapGetters, mapMutations } from 'vuex'
import { mapTwoWayState } from 'spyfu-vuex-helpers'
import { twoWayMap } from '@/store'
import tile from '@/components/tile/fc_tile.vue'
import fileCreator from "@/components/fileUploader/fileCreator.vue"
import RainbowSelector from '@/components/selector/rainbowSelector.vue'
import VueProgressBar from 'vue-progressbar'



export default {
  name: 'RTables',
  components: {
    FileUploader,
    'fc-textarea': fcTextarea,
    'template-modal': templateModal,
    'fc-tile': tile,
    fileCreator,
    'rainbow-selector': RainbowSelector
  },
  data: function () {
    return {
      loading: false,
      helpDismissedMessage: false,
      supported: ["MD5", "SHA1", "SHA2-224", "SHA2-256", "SHA2-512", "SHA2-384"],
      hashTypes: [],
      charsetTypes: [{ name: 'LOWERCASE', characters: 'abcdefghijklmnopqrstuvwxyz' }, { name: 'UPPERCASE', characters: 'abcdefghijklmnopqrstuvwxyz'.toUpperCase() },
      { name: 'LETTERS', characters: 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.toUpperCase() },
      { name: 'ALPHANUMERIC', characters: 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.toUpperCase() + '0123456789' },
      { name: 'ALL ', characters: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~' }],
      headers: [
        { text: 'Name', align: 'start', value: 'name' },
        { text: 'Charset range', value: 'range', align: 'end' },
        { text: 'Hash algorithm', value: 'algorithm', align: 'end' },
        { text: 'Success rate', value: 'number', align: 'end' },
        { text: 'Coverage', value: 'coverage', align: 'end' },
        { text: 'Actions', value: 'actions', align: 'end', sortable: false }
      ],
      working: false,
      rainbowTables: [],
      keyspace: null,
      hashListError: false,
      selectedTemplateName: '',
      loading: true,
      saving: false,
      dialog: false,
      estimate: 0,
      MinPlaintextLen: 5,
      MinPlaintextLenBrowse: 5,
      MaxPlaintextLen: 10,
      MaxPlaintextLenBrowse: 10,
      charsetType: null,
      CharsetTypeBrowse: null,
      hashTypeBrowse: null,
      RowCount: 1000,
      ColumnCount: 1000,
      generating: false,
      hash_input: true,
      message: '',
      filename: '',
      generated: false,
      search: '',
      wutthresh: 180, // minimum reccomended seconds per WU
      confirmpurge: !localStorage.hasOwnProperty('confirmpurge') || localStorage.getItem('confirmpurge') == 'true',
      showContent: false,
      templates: [
        {
          name: 'Empty',
          id: 0
        }
      ],
      addnew: false,
      gotBinaryHash: false,
      IDs: [],
      passwords: [],
      progress: 0
    }
  },
  computed: {
    ...mapState('jobForm', ['selectedTemplate']),
    ...mapTwoWayState('jobForm', twoWayMap([
      'step', 'attackSettingsTab', 'validatedHashes', 'name', 'inputMethod', 'hashList', 'hashType', 'ignoreHashes', 'startDate', 'endDate', 'template', 'comment', 'hosts', 'startNow', 'endNever', 'timeForJob', 'rainbows'
    ])),
    ...mapGetters('jobForm', ['jobSettings', 'valid', 'validAttackSpecificSettings', 'keyspaceKnown']),
    templateItems() {
      return this.templates.map((t, i) => ({ text: t.template, value: i }))
    },
    invalidHashes() {
      return this.validatedHashes.filter(h => h.result !== 'OK')
    },
    dev() {
      return localStorage.getItem('testmode') == 'true'
    },
    helpAlreadyDismissed() {
      return localStorage.getItem('dismissedHelp') == 'true'
    },
    downloadTable() {
      if (this.generated) {
        if (this.filename.substring(this.filename.length - 4) != '.csv') {
          return this.$serverAddr + '/rainbowTables/download/' + this.filename + '.csv'
        }
        else {
          return this.$serverAddr + '/rainbowTables/download/' + this.filename
        }
      }
      else {
        return null
      }
    },
    getPasswords() {
      return this.passwords
    }
  },
  mounted: function () {
    this.loadSettings()
    this.getHashTypes()
    this.startDate = this.$moment().format('YYYY-MM-DDTHH:mm')
    this.endDate = this.$moment().format('YYYY-MM-DDTHH:mm')
    this.fetchTemplates()
    this.loadAllRainbowTables()
  },
  watch: {
    filename(newValue) {
      this.generated = false;
    }
  },
  methods: {
    ...mapMutations('jobForm', ['applyTemplate']),
    async loadSettings() {
      this.loading = true
      this.settings = await this.axios.get(this.$serverAddr + '/settings').then(r => r.data)
      this.loading = false
    },
    dismissHelp(toggleFunction) {
      localStorage.setItem('dismissedHelp', true)
      toggleFunction()
      this.helpDismissedMessage = true
    },
    fetchTemplates() {
      this.axios.get(this.$serverAddr + '/template')
        .then((response) => {
          if (response.data && response.data.items) {
            this.templates = [
              { name: 'Empty', id: 0 },
              ...response.data.items
            ]
          }
        })
        .catch(console.error)
    },
    hashTypeFilter({ name, code }, query) {
      const q = query.toLowerCase()
      return name.toLowerCase().includes(q) || code.toLowerCase().includes(q)
    },
    focusTextarea: function () {
      this.$refs.textarea.focus()
    },
    removeUnsupportedHashTypes: function () {
      for (var i = 0; i < this.hashTypes.length; i++) {
        if (!(this.supported.includes(this.hashTypes[i].name))) {
          this.hashTypes.splice(i, 1)
          i--
        }
      }
    },
    validateHashes: function (data = null) {
      if (data === null) {
        data = this.hashList
      }
      var hashesList = data.split('\n')
      if (data.startsWith("BASE64:")) {
        this.gotBinaryHash = true
      } else {
        this.gotBinaryHash = false
      }
      if (this.hashType === null || isNaN(this.hashType.code)) {
        return
      }
      if (data === '') {
        return
      }

      this.axios.post(this.$serverAddr + '/job/verifyHash', {
        'hashtype': this.hashType.code,
        'hashes': data
      }).then((response) => {
        this.hashListError = response.data.error
        this.validatedHashes = response.data.items
      })
    },
    unvalidateHashes: function (data) {
      this.validatedHashes = []
    },
    getHashTypes: function () {
      this.axios.get(this.$serverAddr + '/hashcat/hashTypes').then((response) => {
        this.hashTypes = response.data.hashtypes
        this.removeUnsupportedHashTypes()
      })
    },

    getEstimate: function (chain_len, chain_num, algorithm, charset, max_len) {
      if (this.MinPlaintextLen > this.MaxPlaintextLen) {
        this.hash_input = false
        return
      }
      if (algorithm == null || charset == null) {
        this.hash_input = false
        return
      }
      console.log(algorithm['code'])
      this.hash_input = true
      this.axios.post(this.$serverAddr + '/rainbowTables/estimate', {
        "chain_len": chain_len,
        "chain_num": chain_num,
        "algorithm": algorithm['code'],
        "charset": charset['name'],
        "max_len": max_len
      }).then((response) => {
        this.estimate = response.data['time']
        this.message = 'Estimated time to complete: ' + Math.floor(this.estimate / 60) + ' minutes and ' + (this.estimate % 60) + ' seconds'
      })
    },
    genRainbowTable: function (length_min, length_max, restrictions, algorithm, columns, rows, filename) {
      this.generated = false
      this.loading = true
      this.axios.post(this.$serverAddr + '/rainbowTables/generate', {
        "length_min": length_min,
        "length_max": length_max,
        "restrictions": restrictions['name'],
        "algorithm": algorithm['code'],
        "columns": columns,
        "rows": rows,
        "filename": filename
      }).then((response) => {
        this.loading = false
        this.generated = response.data['status']
        this.loadAllRainbowTables()
      }).catch((error) => {
        // Handle error here if needed
      }).finally(() => {
        this.loading = false
      })
    },
    loadAllRainbowTables: function () {
      this.loading = true
      this.axios.get(this.$serverAddr + '/rainbowTables/loadall').then((response) => {
        this.rainbowTables = response.data;
        this.loading = false
      }).catch((error) => {
        // Handle error here if needed
      }).finally(() => {
        this.loading = false
      })
    },
    CrackEnteredHashes: function (hashList, rainbows) {
      this.loading = true
      for (var i = 0; i < rainbows.length; i++) {
        this.IDs.push(rainbows[i].id)
      }
      this.axios.post(this.$serverAddr + '/rainbowTables/crack', {
        "tables": this.IDs,
        "hashes": hashList
      }).then((response) => {
        this.passwords = response.data;
        this.loading = false
      }).catch((error) => {
        // Handle error here if needed
      }).finally(() => {
        this.loading = false
      })
    }
  }
}
</script>



<style scoped>
.neutral {
  color: unset !important
}

.mw {
  min-width: 300px;
}

.rmw {
  max-width: 900px;
}

.containerAddJob {
  padding: 2em;
  padding-top: 54px;
  position: relative;
  max-width: 1300px;
}

.addJobContent {
  width: 100%;
}

.max500 {
  max-width: 500px;
  width: 100%;
}

.max800 {
  max-width: 800px;
  width: 100%;
}

.max1000 {
  max-width: 1000px;
}

.infobar {
  position: fixed;
  z-index: 5;
  bottom: 1.2em;
  right: 1.2em;
  padding: 0.5em 1.5em;
  border-radius: 2em;
}

.filetype-link {
  color: inherit
}

.hashCeckContainer {
  display: block;
  max-width: 35px;
  overflow: hidden;
}

.mode-btn {
  height: initial !important;
  margin: 1em;
}

.scroller {
  max-height: 400px;
  overflow-y: auto;
}
</style>
