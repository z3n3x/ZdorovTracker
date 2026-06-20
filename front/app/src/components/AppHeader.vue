<script setup lang="ts">
defineProps<{
    title: string
    subtitle?: string
}>()
</script>

<template>
    <div class="app-header">
        <div class="logo-icon">
            <img src="/logo.svg" alt="Logo" class="logo-svg" />
        </div>
        <div class="header-title">{{ title }}</div>
        <div v-if="subtitle" class="header-subtitle">{{ subtitle }}</div>
    </div>
</template>

<style scoped>
.app-header {
    width: fit-content;
    min-height: 40px;
    display: flex;
    flex-direction: row;
    column-gap: 60px;
    align-items: center;
    justify-content: flex-start;
    padding: 0;
}

.logo-icon {
    width: 50px;
    height: 40px;
    flex-shrink: 0;
}

.logo-svg {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.header-title {
    font-family: 'Iosevka Charon', monospace;
    font-size: 16px;
    font-weight: 400;
    color: #000;
    text-align: left;
}

.header-subtitle {
    font-family: 'Iosevka Charon', monospace;
    font-size: 16px;
    font-weight: 400;
    color: #808080;
    text-align: left;
    width: 697px;
}
</style>