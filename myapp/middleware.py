import time
from http.client import responses

from django.http import HttpResponseForbidden


class LogRequestMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self, request):
        #process before
        print(f"[Middleware] Request Path:{request.path}")
        response=self.get_response(request)

        #process after
        print(f"[Middleware] Response Status:{response.status_code}")

        return response


class TimeMiddleware:
    def __init__(self,get_response):
        self.get_response=get_response

    def __call__(self,request):
        start_time=time.time()
        response=self.get_response(request)
        duration=time.time()-start_time
        print(f"MW Req took {duration:.2f} sec")
        return response

# class BlockIpMiddleware:
#     BLOCKED_IPS=['127.0.0.1']
#     def __init__(self,get_response):
#         self.get_response=get_response
#
#     def __call__(self,request):
#         ip=request.META.get('REMOTE_ADDR')
#         if ip in self.BLOCKED_IPS:
#             return HttpResponseForbidden("your ip is blocked")
#         return self.get_response(request)