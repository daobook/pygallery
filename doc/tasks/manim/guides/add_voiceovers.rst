###########################
为视频添加配音
###########################

创建带有配音的完整视频比创建纯视觉的 Manim 场景要复杂一些。在视频渲染完成后，必须使用 `视频编辑软件 <https://en.wikipedia.org/wiki/List_of_video_editing_software>`__ 来添加配音。这个过程可能既困难又耗时，因为它需要大量的规划和准备工作。

为了简化为视频添加配音的过程，我们创建了 `Manim Voiceover <https://voiceover.manim.community>`__，这是一个插件，允许你直接在 Python 中为场景添加配音。要安装它，请运行：

.. code-block:: bash

    pip install "manim-voiceover[azure,gtts]"

访问 `安装页面 <https://voiceover.manim.community/en/latest/installation.html>`__ 以获取有关如何安装 Manim Voiceover 的更多详细信息。

基本用法
###########

Manim Voiceover 允许你...

- 直接在 Python 中为 Manim 视频添加配音，无需使用视频编辑器。
- 通过简单的命令行界面在渲染过程中使用麦克风录制配音。
- 使用来自各种免费和专有服务的自动生成的 AI 语音开发动画。

它提供了非常简单的 API，允许你指定配音脚本，然后在渲染过程中录制它：

.. code-block:: python

    from manim import *
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.recorder import RecorderService


    # Simply inherit from VoiceoverScene instead of Scene to get all the
    # voiceover functionality.
    class RecorderExample(VoiceoverScene):
        def construct(self):
            # You can choose from a multitude of TTS services,
            # or in this example, record your own voice:
            self.set_speech_service(RecorderService())

            circle = Circle()

            # Surround animation sections with with-statements:
            with self.voiceover(text="This circle is drawn as I speak.") as tracker:
                self.play(Create(circle), run_time=tracker.duration)
                # The duration of the animation is received from the audio file
                # and passed to the tracker automatically.

            # This part will not start playing until the previous voiceover is finished.
            with self.voiceover(text="Let's shift it to the left 2 units.") as tracker:
                self.play(circle.animate.shift(2 * LEFT), run_time=tracker.duration)

要开始使用 Manim Voiceover，请访问 `快速入门指南 <https://voiceover.manim.community/en/latest/quickstart.html>`__。

访问 `示例画廊 <https://voiceover.manim.community/en/latest/examples.html>`__，查看一些 Manim Voiceover 的实际应用示例。
