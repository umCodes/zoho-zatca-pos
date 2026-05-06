
import { createContext, useContext } from "react";
import type { Item } from "../types";
import type { CartEntry } from "../providers/CartProvider";

interface CartContextType {
    cart: CartEntry[];
    setCart: React.Dispatch<React.SetStateAction<CartEntry[]>>;
    addToCart: (item: Item) => void;
    removeFromCart: (id: string) => void;
    updateCartItem: (id: string, updatedFields: Partial<Item>) => void;
}

export const CartContext = createContext<CartContextType | undefined>(undefined);


export const useCart = (): CartContextType => {
    const context = useContext(CartContext);      
    if (!context) {
        throw new Error("useCart must be used within a CartProvider");
    }
    return context;
};