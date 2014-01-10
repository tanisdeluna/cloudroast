"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import ImageMemberStatus
from cloudroast.images.fixtures import ImagesFixture


class UnsharePreviouslySharedImageTest(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_unshare_previously_shared_image(self):
        """@summary: Unshare previously shared image between two users.

        1. Register an image as tenant
        2. Verify that alternative tenant cannot access the image
        3. Add alternative tenant as a member of the image
        4. Verify that alternative tenant can now access the image
        5. Update alternative tenant membership status to 'accepted' for image
        6. Verify that the image belongs to alternative tenant list of images
        7. Remove alternative tenant as a member of the image
        8. Verify that the list of members for the image is empty
        9. Verify that the image does not belong to alternative tenant list
            of images
        """

        image = self.images_behavior.create_new_image()
        alt_tenant_id = self.alt_access_data.token.tenant.id_

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 404)

        response = self.images_client.add_member(image_id=image.id_,
                                                 member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 200)
        member = response.entity
        self.assertEqual(member.member_id, alt_tenant_id)
        self.assertEqual(member.status, ImageMemberStatus.PENDING)

        response = self.alt_images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        new_image = response.entity
        self.assertEqual(new_image, image)

        response = self.alt_images_client.update_member(
            image_id=image.id_, member_id=alt_tenant_id,
            status=ImageMemberStatus.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        updated_member = response.entity
        self.assertEqual(updated_member.member_id, alt_tenant_id)
        self.assertEqual(updated_member.status, ImageMemberStatus.ACCEPTED)

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertIn(image, images)

        response = self.images_client.delete_member(image_id=image.id_,
                                                    member_id=alt_tenant_id)
        self.assertEqual(response.status_code, 204)

        members_ids = self.images_behavior.get_member_ids(image_id=image.id_)
        self.assertEqual(members_ids, [])

        response = self.alt_images_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertNotIn(image, images)