from pydantic import BaseModel
from typing import Literal, List
from uuid import UUID


class RewardSimulationDto(BaseModel):
    user_guid: UUID
    library_guid: UUID
    tier_level: int
    progress_type: Literal["HALF", "FULL"]


SIMULATION_TEST_NOTES: List[dict] = [
    {
        "sequence_no": 1,
        "content_text": "The Deep Work Hypothesis: The ability to perform deep work is becoming increasingly rare at exactly the same time it is becoming increasingly valuable in our economy. As a consequence, the few who cultivate this skill, and then make it the core of their working life, will thrive.",
    },
    {
        "sequence_no": 2,
        "content_text": "This feels like a direct challenge. I spend so much time in \"reactive\" mode\u2014answering messages and fixing minor bugs\u2014that I wonder if I'm actually building the \"rare\" value Newport is talking about.",
    },
    {
        "sequence_no": 3,
        "content_text": "Shallow Work: Noncognitively demanding, logistical-style tasks, often performed while distracted. These efforts tend not to create much new value in the world and are easy to replicate.",
    },
    {
        "sequence_no": 4,
        "content_text": "\"Easy to replicate\" is the scary part. If 80% of my day is Slack and email, is my career essentially replaceable by anyone with a decent internet connection?",
    },
]


SIMULATION_TEST_TRANSCRIPTS: List[dict] = [
    {
        "sender": "user",
        "msg_content": "Hey, I've been sitting with that second note for a few minutes. Newport's idea of 'easy to replicate' work is really bothering me. If I'm honest, most of my day feels like that. Does that mean the actual value I'm contributing right now is low, even if I'm busy all day?",
    },
    {
        "sender": "assistant",
        "msg_content": "It's a heavy realization to face, isn't it? The distinction between 'being busy' and 'producing value' is exactly what Newport wants us to grapple with. Looking at your reflection on that note, you mentioned feeling 'replaceable' because of those logistical tasks. If you were to stop doing the shallow work today\u2014the emails, the quick fixes\u2014what is the one 'deep' skill you have that would be the hardest for someone else to step in and replicate tomorrow?",
    },
    {
        "sender": "user",
        "msg_content": "I think it's the high-level architecture work\u2014designing how complex systems talk to each other without breaking. But I only get to do that for maybe an hour a day because the 'shallow' stuff is so loud. It feels like I'm a chef who spends all his time washing dishes.",
    },
    {
        "sender": "assistant",
        "msg_content": "That's a perfect analogy. The 'chef' work is where the rarity lies. If that architectural design is your core value, Newport would argue that your one hour of 'deep' work is actually more economically significant than the other seven hours of 'dishwashing.' In your last session, you managed two hours of focus; did you notice a shift in the quality of your system designs when you finally silenced the noise?",
    },
    {
        "sender": "user",
        "msg_content": "Definitely. I found a massive logic flaw in 20 minutes that I probably would have missed for a week if I was multitasking. But I still feel this guilt\u2014like if I don't reply to a message in ten minutes, I'm failing the team. How do I balance 'Deep Work' with the reality of a collaborative environment?",
    },
    {
        "sender": "assistant",
        "msg_content": "That guilt is the 'Preservationist's Dilemma' applied to your professional reputation\u2014trying to preserve the image of being 'always available' at the cost of being 'exceptionally valuable'. Newport suggests that 'Busyness as a Proxy for Productivity' is a trap. If you could communicate to your team that you're going into a deep session for just two hours, what is the biggest 'shallow' fear holding you back from actually doing it?",
    },
    {
        "sender": "user",
        "msg_content": "I guess I'm afraid that the perception of my reliability will break. It's easier to be 'the fast replier' than 'the deep thinker.'",
    },
    {
        "sender": "assistant",
        "msg_content": "That's a profound insight. You're choosing the easier path of perceived reliability over the harder path of true mastery. But consider this: is a chef more reliable because he washes dishes quickly, or because the meal is perfect every time? If we set a 90-minute 'Monk Mode' timer right now, what is one architectural problem you could tackle that would prove to you that the deep work is worth the silence?",
    },
    {
        "sender": "user",
        "msg_content": "I want to map out the state machine for the new orchestration module. It's been messy in my head for days.",
    },
    {
        "sender": "assistant",
        "msg_content": "A clean state machine is the ideal candidate for deep work\u2014it requires the kind of mental clarity that shallow work actively destroys. I'll initiate the Focus Module for 90 minutes and silence your notifications. I'll be here if you need to talk through a logic block, but otherwise, the digital world is officially on pause. Ready to find that flow state?",
    },
]
