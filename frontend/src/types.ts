

export type Item = {
    item_id: string;
    name: string;
    status: string;
    description: string;
    rate: number;
    unit: string;
    tax_id: string;
    tax_name: string;
    tax_percentage: number;
    sku: string;
    qty?: number;
}





export type CartRow = {
  item_id: string
  name: string
  rate: number      // VAT-inclusive
  quantity: number
  unit: string
}

export type ToastState = {
  message: string
  type: 'success' | 'error'
}

export type Lang = 'en' | 'ar' | 'am'