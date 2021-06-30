
#ifndef __GST_MESSAGE_H__
#define __GST_MESSAGE_H__
 
#include <gst/gst.h>

#define GST_MESSAGE_META_TYPE       (gst_message_api_get_type())
#define GST_MESSAGE_META_IMPL_NAME   "GstMessageMeta"
#define GST_MESSAGE_META_TAG         "gst_message_meta"
#define GST_MESSAGE_META_API_NAME    "GstMessageMetaAPI"


typedef struct _GstMessageMeta       GstMessageMeta;
typedef struct _GstMessage    GstMessage    ; 


struct _GstMessage {     
    guint64 sequence_number;    
    guint64 timestamp;    
};

struct _GstMessageMeta {
    GstMeta          gstMeta;  
    GstMessage    message;
};  



GType gst_message_api_get_type(void);

const GstMetaInfo *gst_message_meta_get_info(void);
 
GstMessageMeta* gst_buffer_add_message( GstBuffer *buffer, GstMessage *gstMsg);

gboolean gst_buffer_remove_message(GstBuffer *buffer);

GstMessage *gst_buffer_get_message(GstBuffer *buffer);
 

#endif 