<template>
    <div class="max-w-4xl mx-auto p-4 bg-gray-50">
      <h2 class="text-3xl font-semibold text-center mb-8 text-gray-800">Life Timeline</h2>
      <div class="relative">
        <div class="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
        <transition-group name="fade" tag="div">
          <div
            v-for="(event, index) in timeline"
            :key="index"
            class="mb-8 flex items-start"
          >
            <div class="bg-white rounded-full p-2 shadow-md z-10 mr-4">
              <component :is="event.icon" class="w-6 h-6" />
            </div>
            <div class="bg-white p-4 rounded-lg shadow-md flex-grow">
              <div class="flex justify-between items-start mb-2">
                <h3 class="text-xl font-semibold text-gray-800">{{ event.event }}</h3>
                <span class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {{ event.date }}
                </span>
              </div>
              <transition name="fade">
                <p v-if="expandedIndex === index" class="text-gray-600 mb-2">
                  {{ event.description }}
                </p>
              </transition>
              <button
                @click="toggleDetails(index)"
                class="text-sm text-blue-600 hover:text-blue-700 focus:outline-none flex items-center mt-2"
              >
                <component :is="expandedIndex === index ? 'ChevronUp' : 'ChevronDown'" class="w-4 h-4 mr-1" />
                {{ expandedIndex === index ? 'Less details' : 'More details' }}
              </button>
            </div>
          </div>
        </transition-group>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { ChevronDown, ChevronUp, Baby, GraduationCap, Briefcase, Heart } from 'lucide-vue-next';
  
  export default {
    name: 'ProfileTimeline',
    props: {
      profileId: {
        type: Number,
        required: true
      }
    },
    components: {
      ChevronDown,
      ChevronUp,
      Baby,
      GraduationCap,
      Briefcase,
      Heart,
    },
    setup(props) {
      const expandedIndex = ref(null);
      const timeline = ref([]);
  
      const fetchTimeline = async () => {
        try {
          const response = await fetch(`http://localhost:5000/api/profile/${props.profileId}/timeline`, {
            credentials: 'include'
          });
          timeline.value = await response.json();
        } catch (error) {
          console.error('Error fetching timeline:', error);
        }
      };
  
      onMounted(fetchTimeline);
  
      const toggleDetails = (index) => {
        expandedIndex.value = expandedIndex.value === index ? null : index;
      };
  
      return {
        timeline,
        expandedIndex,
        toggleDetails,
      };
    },
  };
  </script>
  
  <style scoped>
  .fade-enter-active, .fade-leave-active {
    transition: opacity 0.5s;
  }
  .fade-enter, .fade-leave-to {
    opacity: 0;
  }
  </style>