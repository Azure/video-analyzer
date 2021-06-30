#include "gst_message.h"

#include "stdio.h"
#include "stdlib.h"
#include "string.h"



void gst_message_init(GstMessage *gst_message)
{
    gst_message->sequence_number = 0;    
    gst_message->timestamp = 0;
}

GstMessage* gst_message_empty_message()
{
    static GstMessage message;
    gst_message_init(&message);
    return &message;
}   

GType gst_message_api_get_type(void)
{
    static const gchar *tags[] = { GST_MESSAGE_META_TAG, NULL };
    static volatile GType type;

    if (g_once_init_enter (&type)) {
        GType _type = gst_meta_api_type_register(GST_MESSAGE_META_API_NAME, tags);
        g_once_init_leave(&type, _type);
    }
    return type;
}

static gboolean gst_message_meta_init(GstMeta *meta, gpointer params, GstBuffer *buffer)
{
    GstMessageMeta *gst_meta = (GstMessageMeta *)meta;     
    gst_message_init(&(gst_meta->message));
    
    return TRUE;
}



static void gst_message_meta_free(GstMeta *meta, GstBuffer *buffer)
{
    

}

// Add message to the buffer
GstMessageMeta* gst_buffer_add_message( GstBuffer *buffer, GstMessage *gstMsg)
{   
    const GstMetaInfo *meta_info = gst_message_meta_get_info(); 
    GstMessageMeta *gstmeta = (GstMessageMeta *)gst_buffer_add_meta(buffer, meta_info, NULL);   

    gstmeta->message.sequence_number = gstMsg->sequence_number;     
    gstmeta->message.timestamp = gstMsg->timestamp;

    return gstmeta;
}

static gboolean gst_message_meta_transform(GstBuffer *dest_buf, GstMeta *src_meta, GstBuffer *src_buf, GQuark type, gpointer data)
{
    
    GstMessageMeta *gst_srcmeta = (GstMessageMeta *)src_meta;
    GstMessageMeta *gst_destmeta = gst_buffer_add_message(dest_buf, &(gst_srcmeta->message));
    
    return TRUE;
}

const GstMetaInfo *gst_message_meta_get_info(void)
{
    static const GstMetaInfo *metainfo = NULL;
 
    if (g_once_init_enter (&metainfo)) {

        const GstMetaInfo *meta = gst_meta_register (gst_message_api_get_type(), 
                                                     GST_MESSAGE_META_IMPL_NAME,           
                                                     sizeof (GstMessageMeta),    
                                                     (GstMetaInitFunction)gst_message_meta_init,
                                                     (GstMetaFreeFunction) gst_message_meta_free,
                                                     (GstMetaTransformFunction)gst_message_meta_transform);
        g_once_init_leave (&metainfo, meta);
    }
    return metainfo;
}

// Gets message from the buffer
GstMessage *gst_buffer_get_message(GstBuffer *buffer)
{
    GstMessageMeta *gstmeta = (GstMessageMeta *)gst_buffer_get_meta((buffer), GST_MESSAGE_META_TYPE);
    
    if (gstmeta == NULL)
        return gst_message_empty_message();
    else
        return &(gstmeta->message);       
}


// Removes message from buffer
gboolean gst_buffer_remove_message(GstBuffer *buffer)
{   
    GstMessageMeta *gstmeta = (GstMessageMeta *)gst_buffer_get_meta((buffer), GST_MESSAGE_META_TYPE);

    if (gstmeta == NULL)
        return TRUE;
    
    if ( !gst_buffer_is_writable(buffer))
        return FALSE;
    
    return gst_buffer_remove_meta(buffer, &(gstmeta->gstMeta));
}