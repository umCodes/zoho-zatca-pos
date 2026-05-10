import { useState } from "react";
import type { Item } from "../types";
import { CartContext } from "../context/CartContext";


export interface CartEntry extends Item{
  qty: number;
  line_id: string
}

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [cart, setCart] = useState<CartEntry[]>([]);

    const addToCart = (item: Item) => {

    setCart(prev => {

        const priceInCents = Math.round(item.price * 100);
        // +15%
        const taxedPriceInCents = Math.round((priceInCents * 115) / 100);
        return [
            ...prev,
            {
                ...item,
                price: taxedPriceInCents / 100,
                qty: item.qty ?? 1,
                line_id: crypto.randomUUID(),
            }];
    });
  };

    const removeFromCart = (id: string) => {
        setCart(prev => prev.filter(item => item.line_id !== id));
    };
    
    const updateCartItem = (id: string, updatedFields: Partial<Item>) => {
        setCart(prev => prev.map(item => item.line_id === id ? { ...item, ...updatedFields } : item));
    };
    
    return (
        <CartContext.Provider value={{ cart, setCart, addToCart, removeFromCart, updateCartItem }}>
            {children}
        </CartContext.Provider>
    );
};
