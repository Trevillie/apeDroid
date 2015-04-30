.class public LInjector;
.super Ljava/lang/Object;
.source "Injector.java"


# static fields
.field private static log_content:Ljava/lang/String;

.field private static log_tag:Ljava/lang/String;

.field private static start_content:Ljava/lang/String;

.field private static start_tag:Ljava/lang/String;


# direct methods
.method static constructor <clinit>()V
    .registers 1

    .prologue
    .line 4
    const-string v0, "Trevillie"

    sput-object v0, LInjector;->log_tag:Ljava/lang/String;

    .line 5
    const-string v0, "This is for the test of log cleaning functionality."

    sput-object v0, LInjector;->log_content:Ljava/lang/String;

    .line 6
    const-string v0, "apeDroid"

    sput-object v0, LInjector;->start_tag:Ljava/lang/String;

    .line 7
    const-string v0, "This is for the test of app startup timing."

    sput-object v0, LInjector;->start_content:Ljava/lang/String;

    return-void
.end method

.method public constructor <init>()V
    .registers 1

    .prologue
    .line 3
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static main([Ljava/lang/String;)V
    .registers 1

    .prologue
    .line 10
    invoke-static {}, LInjector;->test_logging()V

    .line 11
    return-void
.end method

.method public static test_logging()V
    .registers 2

    .prologue
    .line 14
    sget-object v0, LInjector;->log_tag:Ljava/lang/String;

    sget-object v1, LInjector;->log_content:Ljava/lang/String;

    invoke-static {v0, v1}, Landroid/util/Log;->v(Ljava/lang/String;Ljava/lang/String;)I

    .line 15
    sget-object v0, LInjector;->log_tag:Ljava/lang/String;

    sget-object v1, LInjector;->log_content:Ljava/lang/String;

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 16
    sget-object v0, LInjector;->log_tag:Ljava/lang/String;

    sget-object v1, LInjector;->log_content:Ljava/lang/String;

    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 17
    sget-object v0, LInjector;->log_tag:Ljava/lang/String;

    sget-object v1, LInjector;->log_content:Ljava/lang/String;

    invoke-static {v0, v1}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 18
    sget-object v0, LInjector;->log_tag:Ljava/lang/String;

    sget-object v1, LInjector;->log_content:Ljava/lang/String;

    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 19
    return-void
.end method

.method public static test_startup_time()V
    .registers 2

    .prologue
    .line 22
    sget-object v0, LInjector;->start_tag:Ljava/lang/String;

    sget-object v1, LInjector;->start_content:Ljava/lang/String;

    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 23
    return-void
.end method
