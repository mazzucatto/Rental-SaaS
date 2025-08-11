import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Users, 
  Calendar, 
  DollarSign, 
  TrendingUp, 
  TrendingDown,
  Clock,
  CheckCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, tenant } = useAuth();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const data = await api.getDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Erro ao carregar dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  // Dados de exemplo para os gráficos
  const monthlyRevenue = [
    { month: 'Jan', revenue: 4000 },
    { month: 'Fev', revenue: 3000 },
    { month: 'Mar', revenue: 5000 },
    { month: 'Abr', revenue: 4500 },
    { month: 'Mai', revenue: 6000 },
    { month: 'Jun', revenue: 5500 },
  ];

  const reservationStatus = [
    { name: 'Confirmadas', value: 45, color: '#10b981' },
    { name: 'Pendentes', value: 25, color: '#f59e0b' },
    { name: 'Ativas', value: 20, color: '#3b82f6' },
    { name: 'Canceladas', value: 10, color: '#ef4444' },
  ];

  const topItems = [
    { name: 'Furadeira Elétrica', rentals: 15 },
    { name: 'Betoneira 400L', rentals: 12 },
    { name: 'Andaime Metálico', rentals: 10 },
    { name: 'Compressor de Ar', rentals: 8 },
    { name: 'Martelo Demolidor', rentals: 6 },
  ];

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {
    total_items: 0,
    active_items: 0,
    total_customers: 0,
    reservations: { confirmed: 0, pending: 0, active: 0, completed: 0, cancelled: 0 }
  };

  const totalReservations = Object.values(stats.reservations).reduce((a, b) => a + b, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Bem-vindo de volta, {user?.first_name || user?.username}!</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Button onClick={loadDashboardData}>
            Atualizar Dados
          </Button>
        </div>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Itens</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_items}</div>
            <p className="text-xs text-muted-foreground">
              {stats.active_items} ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Clientes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_customers}</div>
            <p className="text-xs text-muted-foreground">
              Clientes cadastrados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Reservas</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalReservations}</div>
            <p className="text-xs text-muted-foreground">
              {stats.reservations.active} ativas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Receita do Mês</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ 12.450</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +12% em relação ao mês anterior
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Receita Mensal */}
        <Card>
          <CardHeader>
            <CardTitle>Receita Mensal</CardTitle>
            <CardDescription>
              Evolução da receita nos últimos 6 meses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={monthlyRevenue}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => [`R$ ${value}`, 'Receita']} />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Status das Reservas */}
        <Card>
          <CardHeader>
            <CardTitle>Status das Reservas</CardTitle>
            <CardDescription>
              Distribuição das reservas por status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={reservationStatus}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {reservationStatus.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Seções adicionais */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Itens Mais Alugados */}
        <Card>
          <CardHeader>
            <CardTitle>Itens Mais Alugados</CardTitle>
            <CardDescription>
              Top 5 itens com mais locações este mês
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topItems.map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600">
                        {index + 1}
                      </span>
                    </div>
                    <span className="font-medium">{item.name}</span>
                  </div>
                  <Badge variant="secondary">
                    {item.rentals} locações
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Reservas Recentes */}
        <Card>
          <CardHeader>
            <CardTitle>Reservas Recentes</CardTitle>
            <CardDescription>
              Últimas reservas criadas no sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData?.recent_reservations?.slice(0, 5).map((reservation) => (
                <div key={reservation.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Calendar className="h-4 w-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium">{reservation.reservation_code}</p>
                      <p className="text-sm text-gray-500">
                        {reservation.customer?.full_name}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge 
                      variant={
                        reservation.status === 'confirmed' ? 'default' :
                        reservation.status === 'pending' ? 'secondary' :
                        reservation.status === 'active' ? 'default' : 'destructive'
                      }
                    >
                      {reservation.status}
                    </Badge>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(reservation.created_at).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>
              )) || (
                <p className="text-gray-500 text-center py-4">
                  Nenhuma reserva recente
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Próximas Reservas */}
      <Card>
        <CardHeader>
          <CardTitle>Próximas Reservas</CardTitle>
          <CardDescription>
            Reservas que começam nos próximos dias
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {dashboardData?.upcoming_reservations?.map((reservation) => (
              <div key={reservation.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <Clock className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="font-medium">{reservation.item?.name}</p>
                    <p className="text-sm text-gray-500">
                      Cliente: {reservation.customer?.full_name}
                    </p>
                    <p className="text-sm text-gray-500">
                      Código: {reservation.reservation_code}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    {new Date(reservation.start_date).toLocaleDateString('pt-BR')}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(reservation.start_date).toLocaleTimeString('pt-BR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                  <Badge variant="outline" className="mt-1">
                    {reservation.status}
                  </Badge>
                </div>
              </div>
            )) || (
              <p className="text-gray-500 text-center py-8">
                Nenhuma reserva próxima
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

