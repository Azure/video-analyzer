
#ifndef __gst_ava_MESSAGE_H__
#define __gst_ava_MESSAGE_H__
 
#include <gst/gst.h>

#define gst_ava_MESSAGE_META_TYPE       (gst_ava_message_api_get_type())
#define gst_ava_MESSAGE_META_IMPL_NAME   "GstAVAMessageMeta"
#define gst_ava_MESSAGE_META_TAG         "gst_ava_message_meta"
#define gst_ava_MESSAGE_META_API_NAME    "GstAVAMessageMetaAPI"


typedef struct _GstAVAMessageMeta       GstAVAMessageMeta;
typedef struct _GstAVAMessage    GstAVAMessage    ; 


struct _GstAVAMessage {     
    guint64 sequence_number;    
    guint64 timestamp;    
};

struct _GstAVAMessageMeta {
    GstMeta          gstMeta;  
    GstAVAMessage    message;
};  



GType gst_ava_message_api_get_type(void);

const GstMetaInfo *gst_ava_message_meta_get_info(void);
 
GstAVAMessageMeta* gst_ava_buffer_add_message( GstBuffer *buffer, GstAVAMessage *gstavaMsg);

gboolean gst_ava_buffer_remove_message(GstBuffer *buffer);

GstAVAMessage *gst_ava_buffer_get_message(GstBuffer *buffer);
 

#endif 