from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from .models import Product, Category, HeroBanner, OrderItem
from .cart import Cart
from .forms import OrderCreateForm

def home(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
    categories = Category.objects.filter(parent__isnull=True)
    
    banner_left = HeroBanner.objects.filter(position='LEFT', is_active=True).first()
    banner_center = HeroBanner.objects.filter(position='CENTER', is_active=True).first()
    banner_right = HeroBanner.objects.filter(position='RIGHT', is_active=True).first()
    
    sports_category = Category.objects.filter(name__icontains='sport').first()
    sports_products = Product.objects.filter(categories=sports_category, is_active=True)[:6] if sports_category else []

    watches_category = Category.objects.filter(name__icontains='watch').first()
    watches_products = Product.objects.filter(categories=watches_category, is_active=True)[:6] if watches_category else []

    kitchen_category = Category.objects.filter(name__icontains='kitchen').first()
    kitchen_products = Product.objects.filter(categories=kitchen_category, is_active=True)[:8] if kitchen_category else []

    context = {
        'products': products,
        'categories': categories,
        'banner_left': banner_left,
        'banner_center': banner_center,
        'banner_right': banner_right,
        'sports_products': sports_products,
        'watches_products': watches_products,
        'kitchen_products': kitchen_products,
    }
    return render(request, 'store/home.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    subcategories = category.subcategories.all()
    product_list = Product.objects.filter(
        Q(categories=category) | Q(categories__in=subcategories),
        is_active=True
    ).distinct().order_by('-created_at') 
    
    paginator = Paginator(product_list, 20) 
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'store/category_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        ).distinct()

    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'store/search_results.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    main_image = product.images.filter(is_main=True).first()
    if not main_image:
        main_image = product.images.first()
    
    context = {
        'product': product,
        'main_image': main_image,
    }
    return render(request, 'store/product_detail.html', context)

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

@require_POST
def cart_add(request, item_id):
    cart = Cart(request)
    variant_id = request.POST.get('variant_id', item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart.add(item_id=variant_id, quantity=quantity, override_quantity=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total_items': len(cart), 
            'message': 'Added to cart successfully!'
        })
        
    return redirect('cart_detail')

def cart_remove(request, item_id):
    cart = Cart(request)
    cart.remove(item_id)
    return redirect('cart_detail')

@require_POST
def cart_update(request, item_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(item_id=item_id, quantity=quantity)
    return redirect('cart_detail')
    
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('home') 

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            # NEW: Attach the logged-in user to the order
            if request.user.is_authenticated:
                order.user = request.user
                
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    variant=item['variant'],
                    price=item['price'],
                    quantity=item['quantity'],
                    wholesaler=item['product'].wholesaler 
                )
            
            cart.clear()
            request.session['order_id'] = order.id
            return redirect('checkout_success')
    else:
        form = OrderCreateForm()

    return render(request, 'store/checkout.html', {'cart': cart, 'form': form})

def checkout_success(request):
    order_id = request.session.get('order_id', None)
    return render(request, 'store/checkout_success.html', {'order_id': order_id})