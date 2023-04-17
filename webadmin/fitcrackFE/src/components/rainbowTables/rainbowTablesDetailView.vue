<!--
   * Author : see AUTHORS
   * Licence: MIT, see LICENSE
-->

<template>
    <div>
        <v-breadcrumbs v-if="data != null" :items="
            [
                { text: 'RainbowTables', to: { name: 'rainbowTables' }, exact: true },
                { text: data.name }
            ]" divider="/" />

        <v-container>
            <fc-tile title="Rainbow table set" :loading="data == null" class="mx-2 dictContentContainer mb-4">
                <v-list v-if="data != null">
                    <v-list-item>
                        <v-list-item-action>
                            Name:
                        </v-list-item-action>
                        <v-list-item-content>
                            <v-list-item-title class="text-right">
                                {{ data.name }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-divider />
                    <v-list-item>
                        <v-list-item-action>
                            Chain length:
                        </v-list-item-action>
                        <v-list-item-content>
                            <v-list-item-title class="text-right">
                                {{ data.chain_len }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-divider />
                    <v-list-item>
                        <v-list-item-action>
                            Hashing algorithm used:
                        </v-list-item-action>
                        <v-list-item-content>
                            <v-list-item-title class="text-right">
                                {{ data.algorithm }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-divider />
                    <v-list-item>
                        <v-list-item-action>
                            Characters used:
                        </v-list-item-action>
                        <v-list-item-content>
                            <v-list-item-title class="text-right" v-html="formattedText">
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-divider />
                    <v-list-item>
                        <v-list-item-action>
                            Character range:
                        </v-list-item-action>
                        <v-list-item-content>
                            <v-list-item-title class="text-right">
                                {{ data.range }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-divider />
                    <v-list-item>
                        <v-list-item-action>
                            Times used:
                        </v-list-item-action>
                        <v-list-item-content>
                            <v-list-item-title class="text-right">
                                {{ data.tries }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                    <v-divider />
                    <v-list-item>
                        <v-list-item-action>
                            Successful tries:
                        </v-list-item-action>
                        <v-list-item-content>
                            <v-list-item-title class="text-right">
                                {{ data.successful }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                </v-list>
                <v-row class="mx-2 mb-2">
                    <v-col>
                        <v-btn color="primary" :href="$serverAddr + '/rainbowTables/download/' + data.name" target="_blank"
                            class="ml-2">
                            Download <v-icon right>mdi-download</v-icon>
                        </v-btn>
                    </v-col>
                </v-row>
                <v-divider />
                <div v-if="data != null" class="dictContent pa-2">
                    <code class="code elevation-0">{{ data.data.substring(0, showLength) }}</code>
                </div>
            </fc-tile>
        </v-container>
    </div>
</template>
  
<script>
import tile from '@/components/tile/fc_tile.vue'
export default {
    name: "rainbowTablesDetailView",
    components: {
        'fc-tile': tile
    },
    data: function () {
        return {
            data: null,
            newData: '',
            showLength: 2000,
            loadMore: true
        }
    },
    mounted: function () {
        this.loadData()
        window.addEventListener('scroll', this.handleScroll);
    },
    methods: {
        loadData: function ($state) {
            this.axios.get(this.$serverAddr + '/rainbowTables/' + this.$route.params.id).then((response) => {
                this.data = response.data
            });
        },
        handleScroll() {
            const scrollPosition = window.innerHeight + window.scrollY;
            const pageHeight = document.documentElement.scrollHeight;

            if (scrollPosition >= pageHeight && this.loadMore) {
                // Load more text
                this.showLength += 2000;

                // Stop loading more text if all text is displayed
                if (this.showLength >= this.data.data.length) {
                    this.loadMore = false;
                }
            }
        }
    },
    computed: {
        formattedText() {
            return this.data.restrictions
                .match(/.{1,30}/g)
                .join('<br>');
        }
    }
}
</script>
  
<style scoped>
.dictContentContainer {
    max-width: 800px;
}

.dictContent {
    overflow: auto;
}

.dictContent.editing {
    border: 1px solid;
}

.code::before {
    display: none;
}

.code {
    width: 100%;
    background: transparent;
    color: #000;
    white-space: pre-wrap;
}

.width100 {
    width: 100%;
}

.margintop5 {
    margin-top: 10px;
}
</style>
  