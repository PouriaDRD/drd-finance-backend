from rest_framework.response import Response


class APIResponse:

    @staticmethod
    def success(data=None, message="Success", status_code=200):
        return Response(
            {
                "success": True,
                "message": message,
                "data": data,
            },
            status=status_code,
        )

    @staticmethod
    def error(errors=None, message="Error", status_code=400):
        return Response(
            {
                "success": False,
                "message": message,
                "errors": errors,
            },
            status=status_code,
        )
