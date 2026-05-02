import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductCard from '../ProductCard.vue'

describe('ProductCard.vue', () => {
  it('renders product name and article_id', () => {
    const product = {
      article_id: '12345',
      name: 'Test Product',
      weight_label: '500g'
    }
    const wrapper = mount(ProductCard, {
      props: { product }
    })

    expect(wrapper.text()).toContain('Test Product')
    expect(wrapper.text()).toContain('# 12345')
    expect(wrapper.text()).toContain('500g')
  })

  it('does not render weight_label if not provided', () => {
    const product = {
      article_id: '12345',
      name: 'Test Product'
    }
    const wrapper = mount(ProductCard, {
      props: { product }
    })

    expect(wrapper.find('.bg-tg-bg').exists()).toBe(false)
  })
})
