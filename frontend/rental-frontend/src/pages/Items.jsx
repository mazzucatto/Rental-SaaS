import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye,
  Package,
  DollarSign,
  Clock,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const Items = () => {
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  
  const { hasPermission } = useAuth();

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category_id: '',
    sku: '',
    hourly_price: '',
    daily_price: '',
    weekly_price: '',
    monthly_price: '',
    total_quantity: 1,
    available_quantity: 1,
    min_rental_hours: 1,
    max_rental_days: '',
    requires_deposit: false,
    deposit_amount: '',
    specifications: '',
    is_active: true
  });

  useEffect(() => {
    loadItems();
    loadCategories();
  }, [currentPage, searchTerm, selectedCategory, selectedStatus]);

  const loadItems = async () => {
    try {
      setLoading(true);
      const params = {
        page: currentPage,
        per_page: 10,
        search: searchTerm,
        category_id: selectedCategory,
        status: selectedStatus
      };

      const response = await api.getItems(params);
      setItems(response.items || []);
      setTotalPages(response.pagination?.pages || 1);
    } catch (error) {
      console.error('Erro ao carregar itens:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const response = await api.getCategories();
      setCategories(response || []);
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
    }
  };

  const handleCreateItem = async () => {
    try {
      await api.createItem(formData);
      setShowCreateDialog(false);
      resetForm();
      loadItems();
    } catch (error) {
      console.error('Erro ao criar item:', error);
    }
  };

  const handleEditItem = async () => {
    try {
      await api.updateItem(selectedItem.id, formData);
      setShowEditDialog(false);
      resetForm();
      setSelectedItem(null);
      loadItems();
    } catch (error) {
      console.error('Erro ao editar item:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category_id: '',
      sku: '',
      hourly_price: '',
      daily_price: '',
      weekly_price: '',
      monthly_price: '',
      total_quantity: 1,
      available_quantity: 1,
      min_rental_hours: 1,
      max_rental_days: '',
      requires_deposit: false,
      deposit_amount: '',
      specifications: '',
      is_active: true
    });
  };

  const openEditDialog = (item) => {
    setSelectedItem(item);
    setFormData({
      name: item.name || '',
      description: item.description || '',
      category_id: item.category_id || '',
      sku: item.sku || '',
      hourly_price: item.hourly_price || '',
      daily_price: item.daily_price || '',
      weekly_price: item.weekly_price || '',
      monthly_price: item.monthly_price || '',
      total_quantity: item.total_quantity || 1,
      available_quantity: item.available_quantity || 1,
      min_rental_hours: item.min_rental_hours || 1,
      max_rental_days: item.max_rental_days || '',
      requires_deposit: item.requires_deposit || false,
      deposit_amount: item.deposit_amount || '',
      specifications: item.specifications || '',
      is_active: item.is_active !== false
    });
    setShowEditDialog(true);
  };

  const getStatusBadge = (status, isActive) => {
    if (!isActive) {
      return <Badge variant="secondary">Inativo</Badge>;
    }
    
    switch (status) {
      case 'available':
        return <Badge variant="default">Disponível</Badge>;
      case 'rented':
        return <Badge variant="destructive">Alugado</Badge>;
      case 'maintenance':
        return <Badge variant="secondary">Manutenção</Badge>;
      case 'retired':
        return <Badge variant="outline">Aposentado</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const formatPrice = (price) => {
    if (!price) return '-';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(price);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Itens de Locação</h1>
          <p className="text-gray-600">Gerencie seu catálogo de itens para locação</p>
        </div>
        {hasPermission('manage_items') && (
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Novo Item
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Criar Novo Item</DialogTitle>
                <DialogDescription>
                  Adicione um novo item ao catálogo de locação
                </DialogDescription>
              </DialogHeader>
              
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome do Item</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      placeholder="Ex: Furadeira Elétrica"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sku">SKU</Label>
                    <Input
                      id="sku"
                      value={formData.sku}
                      onChange={(e) => setFormData({...formData, sku: e.target.value})}
                      placeholder="Ex: FUR-001"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Descrição</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    placeholder="Descrição detalhada do item"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">Categoria</Label>
                  <Select value={formData.category_id} onValueChange={(value) => setFormData({...formData, category_id: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione uma categoria" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id.toString()}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="hourly_price">Preço por Hora</Label>
                    <Input
                      id="hourly_price"
                      type="number"
                      step="0.01"
                      value={formData.hourly_price}
                      onChange={(e) => setFormData({...formData, hourly_price: e.target.value})}
                      placeholder="0.00"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="daily_price">Preço por Dia</Label>
                    <Input
                      id="daily_price"
                      type="number"
                      step="0.01"
                      value={formData.daily_price}
                      onChange={(e) => setFormData({...formData, daily_price: e.target.value})}
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="weekly_price">Preço por Semana</Label>
                    <Input
                      id="weekly_price"
                      type="number"
                      step="0.01"
                      value={formData.weekly_price}
                      onChange={(e) => setFormData({...formData, weekly_price: e.target.value})}
                      placeholder="0.00"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="monthly_price">Preço por Mês</Label>
                    <Input
                      id="monthly_price"
                      type="number"
                      step="0.01"
                      value={formData.monthly_price}
                      onChange={(e) => setFormData({...formData, monthly_price: e.target.value})}
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="total_quantity">Quantidade Total</Label>
                    <Input
                      id="total_quantity"
                      type="number"
                      value={formData.total_quantity}
                      onChange={(e) => setFormData({...formData, total_quantity: parseInt(e.target.value)})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="available_quantity">Quantidade Disponível</Label>
                    <Input
                      id="available_quantity"
                      type="number"
                      value={formData.available_quantity}
                      onChange={(e) => setFormData({...formData, available_quantity: parseInt(e.target.value)})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="min_rental_hours">Mín. Horas Locação</Label>
                    <Input
                      id="min_rental_hours"
                      type="number"
                      value={formData.min_rental_hours}
                      onChange={(e) => setFormData({...formData, min_rental_hours: parseInt(e.target.value)})}
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="requires_deposit"
                    checked={formData.requires_deposit}
                    onCheckedChange={(checked) => setFormData({...formData, requires_deposit: checked})}
                  />
                  <Label htmlFor="requires_deposit">Requer Caução</Label>
                </div>

                {formData.requires_deposit && (
                  <div className="space-y-2">
                    <Label htmlFor="deposit_amount">Valor da Caução</Label>
                    <Input
                      id="deposit_amount"
                      type="number"
                      step="0.01"
                      value={formData.deposit_amount}
                      onChange={(e) => setFormData({...formData, deposit_amount: e.target.value})}
                      placeholder="0.00"
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="specifications">Especificações</Label>
                  <Textarea
                    id="specifications"
                    value={formData.specifications}
                    onChange={(e) => setFormData({...formData, specifications: e.target.value})}
                    placeholder="Especificações técnicas do item"
                  />
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleCreateItem}>
                  Criar Item
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Pesquisar itens..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Todas as categorias" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todas as categorias</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.id.toString()}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedStatus} onValueChange={setSelectedStatus}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Todos os status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos os status</SelectItem>
                <SelectItem value="available">Disponível</SelectItem>
                <SelectItem value="rented">Alugado</SelectItem>
                <SelectItem value="maintenance">Manutenção</SelectItem>
                <SelectItem value="retired">Aposentado</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de itens */}
      <Card>
        <CardHeader>
          <CardTitle>Itens Cadastrados</CardTitle>
          <CardDescription>
            Lista de todos os itens disponíveis para locação
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-100 rounded animate-pulse"></div>
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Preços</TableHead>
                  <TableHead>Estoque</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={item.images?.[0]} />
                          <AvatarFallback>
                            <Package className="h-5 w-5" />
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium">{item.name}</p>
                          <p className="text-sm text-gray-500">{item.sku}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {item.category?.name || '-'}
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {item.hourly_price && (
                          <div className="text-sm">
                            <Clock className="inline h-3 w-3 mr-1" />
                            {formatPrice(item.hourly_price)}/h
                          </div>
                        )}
                        {item.daily_price && (
                          <div className="text-sm">
                            <DollarSign className="inline h-3 w-3 mr-1" />
                            {formatPrice(item.daily_price)}/dia
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <span className="font-medium">{item.available_quantity}</span>
                        <span className="text-gray-500">/{item.total_quantity}</span>
                      </div>
                      {item.available_quantity === 0 && (
                        <div className="flex items-center text-red-600 text-xs mt-1">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          Esgotado
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(item.status, item.is_active)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {hasPermission('manage_items') && (
                          <>
                            <Button 
                              variant="ghost" 
                              size="sm"
                              onClick={() => openEditDialog(item)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {/* Paginação */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-gray-500">
                Página {currentPage} de {totalPages}
              </p>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                >
                  Anterior
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                >
                  Próxima
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de edição */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Editar Item</DialogTitle>
            <DialogDescription>
              Edite as informações do item selecionado
            </DialogDescription>
          </DialogHeader>
          
          {/* Mesmo formulário do criar, mas com dados preenchidos */}
          <div className="grid gap-4 py-4">
            {/* Conteúdo igual ao formulário de criação */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Nome do Item</Label>
                <Input
                  id="edit-name"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="Ex: Furadeira Elétrica"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-sku">SKU</Label>
                <Input
                  id="edit-sku"
                  value={formData.sku}
                  onChange={(e) => setFormData({...formData, sku: e.target.value})}
                  placeholder="Ex: FUR-001"
                />
              </div>
            </div>
            {/* Resto dos campos... */}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancelar
            </Button>
            <Button onClick={handleEditItem}>
              Salvar Alterações
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Items;

