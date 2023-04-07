<!--
   * Author : see AUTHORS
   * Licence: MIT, see LICENSE
-->

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
        </fc-tile>
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
                  hint="Select the minimum length of plaintexts" persistent-hint suffix="characters" class="mb-4" />
                <v-text-field :loading="loading" outlined type="number" label="Max plaintext len" min="1" max="30"
                  hint="Select the maximum length of plaintexts" persistent-hint suffix="characters" class="mb-4" />
                <v-text-field :loading="loading" outlined type="number" label="Number of rows" min="1"
                  hint="Select the number of rows" persistent-hint suffix="rows" class="mb-4" />
                <v-text-field :loading="loading" outlined type="number" label="Number of columns" min="1"
                  hint="Select the number of columns" persistent-hint suffix="columns" class="mb-4" />
                <v-autocomplete id="hash-type-select" v-model="hashType" editable validate-on-blur clearable
                  label="Select hash type" :items="hashTypes" item-text="name" :filter="hashTypeFilter" return-object
                  required hide-details single-line flat solo-inverted no-data-text="No matching hash type"
                  @change="validateHashes(null)">
                  <template #item="{ item }">
                    <v-list-item-content>
                      <v-list-item-title><b>{{ item.code }}</b> - {{ item.name }}</v-list-item-title>
                    </v-list-item-content>
                  </template>
                </v-autocomplete>
                <v-autocomplete id="charset-type-select" editable validate-on-blur clearable label="Select charset"
                  :items="charsetTypes" item-text="name" return-object required hide-details single-line flat
                  solo-inverted no-data-text="No matching charset">
                  <template #item="{ item }">
                    <v-list-item-content>
                      <v-list-item-title><b>{{ item.name }}</b></v-list-item-title>
                    </v-list-item-content>
                  </template>
                </v-autocomplete>
              </v-card-text>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import numberFormat from '@/assets/scripts/numberFormat'
import { attackIcon } from '@/assets/scripts/iconMaps'
import combinator from '@/components/job/attacks/combinator.vue'
import FileUploader from "@/components/fileUploader/fileUploader.vue";
import fcTextarea from '@/components/textarea/fc_textarea.vue'
import hostSelector from '@/components/selector/hostSelector.vue'
import templateModal from '@/components/jobTemplate/templateModal.vue'
import dtPicker from '@/components/picker/datetime.vue'

import { mapState, mapGetters, mapMutations } from 'vuex'
import { mapTwoWayState } from 'spyfu-vuex-helpers'
import { twoWayMap } from '@/store'

import { attacks } from '@/store/job-form'


export default {
  name: 'RTables',
  components: {
    FileUploader,
    'combinator': combinator,
    'maskattack': mask,
    'dictionary': dictionary,
    'hybridMaskWordlist': hybridMaskWordlist,
    'hybridWordlistMask': hybridWordlistMask,
    'pcfgAttack': pcfgAttack,
    'princeAttack': princeAttack,
    'fc-textarea': fcTextarea,
    'host-selector': hostSelector,
    'template-modal': templateModal,
    dtPicker
  },
  data: function () {
    return {
      loading: false,
      helpDismissedMessage: false,
      supported: ["MD5", "SHA1", "MD4", "NTLM", "SHA2-256"],
      hashTypes: [],
      letters: 'abcdefghijklmnopqrstuvwxyz',
      charsetTypes: [{ name: 'LOWERCASE', characters: this.letters }, { name: 'UPPERCASE', characters: this.letters },
      { name: 'LETTERS', characters: 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.toUpperCase() }, { name: 'ALPHANUMERIC', characters: 'adsasdvsfd' }],
      showEstimatedTime: false,
      estimatedTime: null,
      keyspace: null,
      gotBinaryHash: false,
      hashListError: false,
      selectedTemplateName: '',
      loading: true,
      saving: false,
      wutthresh: 180, // minimum reccomended seconds per WU
      confirmpurge: !localStorage.hasOwnProperty('confirmpurge') || localStorage.getItem('confirmpurge') == 'true',
      attacks,
      showContent: false,
      templates: [
        {
          name: 'Empty',
          id: 0
        }
      ]
    }
  },
  computed: {
    ...mapState('jobForm', ['selectedTemplate']),
    ...mapTwoWayState('jobForm', twoWayMap([
      'step', 'attackSettingsTab', 'validatedHashes', 'name', 'inputMethod', 'hashList', 'hashType', 'ignoreHashes', 'startDate', 'endDate', 'template', 'comment', 'hosts', 'startNow', 'endNever', 'timeForJob'
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
    }
  },
  mounted: function () {
    this.loadSettings()
    this.getHashTypes()
    this.startDate = this.$moment().format('YYYY-MM-DDTHH:mm')
    this.endDate = this.$moment().format('YYYY-MM-DDTHH:mm')
    if (this.hashList.length > 0) this.validateHashes()
    this.fetchTemplates()
  },
  methods: {
    ...mapMutations('jobForm', ['applyTemplate']),
    numberFormat,
    attackIcon,
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
    beforeRouteLeave(to, from, next) {
      if (!this.saving) next()
    },
    fetchAndApplyTemplate(id) {
      if (id == 0) {
        this.applyTemplate()
        this.selectedTemplateName = ''
        this.$store.commit('jobForm/selectedTemplateMut', 0)
        this.loadSettings()
        return
      }
      this.axios.get(this.$serverAddr + `/template/${id}`)
        .then((response) => {
          if (response.data && response.data.template) {
            const data = JSON.parse(response.data.template)
            this.applyTemplate(data)
            this.selectedTemplateName = data.template
            this.$store.commit('jobForm/selectedTemplateMut', id)
          }
        })
        .catch(console.error)
    },
    hashTypeFilter({ name, code }, query) {
      const q = query.toLowerCase()
      return name.toLowerCase().includes(q) || code.toLowerCase().includes(q)
    },
    subHashtypeChanged: function (key, val) {
      this.hashType.code = this.hashType.code.replace(key, val.code)
      this.validateHashes(null)
    },
    focusTextarea: function () {
      this.$refs.textarea.focus()
    },
    unvalidateHashes: function (data) {
      this.validatedHashes = []
    },
    removeUnsupportedHashTypes: function () {
      for (var i = 0; i < this.hashTypes.length; i++) {
        if (!(this.supported.includes(this.hashTypes[i].name))) {
          console.log(this.hashTypes[i])
          this.hashTypes.splice(i, 1)
          i--
        }
      }
    },
    getHashTypes: function () {
      this.axios.get(this.$serverAddr + '/hashcat/hashTypes').then((response) => {
        this.hashTypes = response.data.hashtypes
        this.removeUnsupportedHashTypes()
      })
    },
    charsetKeys() {
      console.log(item)
      return this.charsetTypes.map((item) => ({ key: Object.keys(item)[0] }));
    },
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
</style>
