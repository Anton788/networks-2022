from django.urls import path
from Products.views import storage, products, search

urlpatterns = [
    path('product/create/', products.CreateProductView.as_view()),
    path('product/create/file/', products.AddProductsFileForProcessingView.as_view()),
    path('product/delete/', products.DeleteProductView.as_view()),
    path('product/update/', products.UpdateProductView.as_view()),
    path('product/get/', products.ReadProductView.as_view()),
    path('product/get/preview/', products.ReadProductView.as_view()),
    path('product/update/get/', products.ReadProductUpdateView.as_view()),
    path('product/update/image/main/', products.SetMainImageView.as_view()),
    path('product/update/image/delete/', products.DeleteImageView.as_view()),
    path('product/update/image/add/', products.AddImageView.as_view()),
    path('image/update/', products.ChangeImageDescriptionView.as_view()),

    path('factory/products/', products.GetFactoryProductsView.as_view()),
    path('factory/products/files/', products.ShowProductsFileForProcessingView.as_view()),
    path('company/products/', products.GetCompanyProductsView.as_view()),
    path('company/products/files/', products.ShowProductsFileForProcessingView.as_view()),

    path('company/products/all/', products.GetCompanyFactoryProductsView.as_view()),

    path('product/update/file/add/', products.AddFileView.as_view()),
    path('product/update/file/delete/', products.DeleteFileView.as_view()),
    path('product/update/available/', products.UpdateAvailableProductView.as_view()),

    path('file/update/', products.ChangeFileInfoView.as_view()),
    
    path('rating/add/', products.CreateUpdateProductRatingView.as_view()),
    path('rating/delete/', products.DeleteProductRatingView.as_view()),
    path('rating/get/list/', products.GetProductRatingListView.as_view()),
    path('rating/get/my/', products.MyProductRatingView.as_view()),

    # ==================== SEARCHING ====================

    path('search/products/name/', search.SearchProductNameView.as_view()),
    path('search/products/', search.SearchProductsView.as_view()),
    path('product/filter/search/', search.CustomSearchProductView.as_view()),
    
    # ==================== STORAGE ====================

    path('create/table/excel/', storage.CreateTableExcelView.as_view()),
    path('upload/image/', storage.UploadImageView.as_view()),

    #path('test/', storage.TestView.as_view()),

    # ==================== PRODUCERS ====================

    path('product/company/producer/set/', products.SetProductCompanyProducersView.as_view()),
    path('product/company/producer/create/', products.CreateProductCompanyProducersView.as_view()),
    path('product/factory/producer/set/', products.SetProductFactoryProducersView.as_view()),
    path('product/factory/producer/create/', products.CreateProductFactoryProducersView.as_view()),
    
]
