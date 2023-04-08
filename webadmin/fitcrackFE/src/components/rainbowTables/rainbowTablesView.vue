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
                  value="5" />

                <v-text-field :loading="loading" outlined type="number" label="Max plaintext len" min="1" max="30"
                  hint="Select the maximum length of plaintexts" persistent-hint suffix="characters" class="mb-4"
                  value="10" />

                <v-text-field :loading="loading" outlined type="number" label="Number of rows" min="1"
                  hint="Select the number of rows" persistent-hint suffix="rows" class="mb-4" value="10000" />

                <v-text-field :loading="loading" outlined type="number" label="Number of columns" min="1"
                  hint="Select the number of columns" persistent-hint suffix="columns" class="mb-4" value="1000" />

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
                <v-text-field :loading="loading" outlined readonly
                  hint="Makes a table generating time estimate based on input values" persistent-hint class="mb-4"
                  value="" style="margin-top: 20px;" />
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
                <v-text-field :loading="loading" outlined type="number" label="Min plaintext len" min="1" max="30"
                  hint="Select the minimum length of plaintexts" persistent-hint suffix="characters" class="mb-4"
                  value="5" />

                <v-text-field :loading="loading" outlined type="number" label="Max plaintext len" min="1" max="30"
                  hint="Select the maximum length of plaintexts" persistent-hint suffix="characters" class="mb-4"
                  value="10" />

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

                <v-data-table
                :headers="headers"
                :items="rainbowTables.items"
                :loading="loading"
                :footer-props="{itemsPerPageOptions: [10,25,50], itemsPerPageText: 'Hcstats per page'}"
                >
                  <template v-slot:item.time="{ item }">
                    {{ $moment.utc(item.time).local().format('DD.MM.YYYY HH:mm') }}
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <a
                          :href="$serverAddr + '/rainbowTables/' + item.id"
                          target="_blank"
                          download
                          v-on="on"
                        >
                          <v-btn icon>
                            <v-icon>mdi-file-download-outline</v-icon>
                          </v-btn>
                        </a>
                      </template>
                      <span>Download</span>
                    </v-tooltip>
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-btn
                          icon
                          @click="deleteRT(item)"
                          v-on="on"
                        >
                          <v-icon color="error">
                            mdi-delete-outline
                          </v-icon>
                        </v-btn>
                      </template>
                      <span>Delete</span>
                    </v-tooltip>
                  </template>
                </v-data-table>
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
import numberFormat from '@/assets/scripts/numberFormat'
import { attackIcon } from '@/assets/scripts/iconMaps'
import combinator from '@/components/job/attacks/combinator.vue'
import FileUploader from "@/components/fileUploader/fileUploader.vue";
import fcTextarea from '@/components/textarea/fc_textarea.vue'
import hostSelector from '@/components/selector/hostSelector.vue'
import templateModal from '@/components/jobTemplate/templateModal.vue'
import mask from '@/components/job/attacks/mask.vue'
import dictionary from '@/components/job/attacks/dictionary.vue'
import hybridMaskWordlist from '@/components/job/attacks/hybridMaskWordlist.vue'
import hybridWordlistMask from '@/components/job/attacks/hybridWordlistMask.vue'
import pcfgAttack from '@/components/job/attacks/pcfg.vue'
import princeAttack from '@/components/job/attacks/prince.vue'
import { mapState, mapGetters, mapMutations } from 'vuex'
import { mapTwoWayState } from 'spyfu-vuex-helpers'
import { twoWayMap } from '@/store'
import tile from '@/components/tile/fc_tile.vue'
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
    'fc-tile': tile,
  },
  data: function () {
    return {
      loading: false,
      helpDismissedMessage: false,
      supported: ["MD5", "SHA1", "MD4", "NTLM", "SHA2-256"],
      hashTypes: [],
      charsetTypes: [{ name: 'LOWERCASE', characters: 'abcdefghijklmnopqrstuvwxyz' }, { name: 'UPPERCASE', characters: 'abcdefghijklmnopqrstuvwxyz'.toUpperCase() },
      { name: 'LETTERS', characters: 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.toUpperCase() },
      { name: 'ALPHANUMERIC', characters: 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.toUpperCase() + '0123456789' },
      { name: 'ALL CHARACTERS ', characters: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~' }],
      headers: [
          {text: 'Name', align: 'start', value: 'name' },
          {text: 'Charset range', value: 'number', align: 'end'},
          {text: 'Hash algorithm', value: 'name', align: 'end'},
          {text: 'Success rate', value: 'number', align: 'end'},
          {text: 'Added', value: 'time', align: 'end'},
          {text: 'Actions', value: 'actions', align: 'end', sortable: false}
      ],
      rainbowTables: [],
      keyspace: null,
      hashListError: false,
      selectedTemplateName: '',
      loading: true,
      saving: false,
      dialog: false,
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
    removeUnsupportedHashTypes: function () {
      for (var i = 0; i < this.hashTypes.length; i++) {
        if (!(this.supported.includes(this.hashTypes[i].name))) {
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
      console.log(this.$serverAddr)
    },
    loadRainbowTables: function () {
        this.dialog= false
        this.loading = true;
        this.axios.get(this.$serverAddr + '/RainbowTables', {}).then((response) => {
          this.rainbowTables = response.data;
          this.loading = false
        })
      },
    deleteRT: function (item) {
        this.$root.$confirm('Delete', `This will remove ${item.name} from your Rainbow Tables. Are you sure?`).then((confirm) => {
          this.loading = true;
          this.axios.delete(this.$serverAddr + '/RTables/' + item.id).then((response) => {
            this.loadRainbowTables()
          })
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
</style>
