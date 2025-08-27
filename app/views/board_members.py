from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models.board_members import BoardMember
from app.models.schools import School
from app.serializers.board_members import BoardMemberListSerializer, BoardMemberSerializer, BoardMemberDetailSerializer
from app.utils.pagination import CustomPagination

class BoardMemberListAPI(APIView):
    def get(self, req):
        """Get all board members"""
        serializer = BoardMemberListSerializer(BoardMember.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, req):
        """Add a new board member"""      
        serializer = BoardMemberDetailSerializer(data=req.data)
        if serializer.is_valid():
            token_data = req.data.get('token_data', {})
            serializer.agency = token_data.get('agency', '')
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BoardMemberListBySchoolAPI(APIView):
    def get(self, req, school_id):
        """Get all board members for a specific school"""
        school = get_object_or_404(School, id=school_id)
        members = BoardMember.objects.filter(schools=school)
        
        serializer = BoardMemberSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BoardMemberAssignToSchoolAPI(APIView):
    def post(self, req, pk):
        """Assign the board member to the school"""
        member = get_object_or_404(BoardMember, id=pk)
        school = get_object_or_404(School, id=req.data['id'])
        member.schools.add(school)
        member.save()

        serializer = BoardMemberDetailSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BoardMemberDetailAPI(APIView):
    def get(self, req, pk):
        """Get details of a specific board member"""
        member = get_object_or_404(BoardMember, id=pk)
        
        serializer = BoardMemberDetailSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, req, pk):
        """Update a board member"""
        member = get_object_or_404(BoardMember, id=pk)
        
        serializer = BoardMemberSerializer(member, data=req.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, req, pk):
        """Delete a board member"""
        member = get_object_or_404(BoardMember, id=pk)
        
        member.delete()
        return Response(
            {"message": "Board member deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        ) 