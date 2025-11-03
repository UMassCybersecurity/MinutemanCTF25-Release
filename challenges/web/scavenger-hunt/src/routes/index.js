const router = require('express').Router();
const path = require('path');

router.get('/',(req,res)=>{
    res.render(path.resolve('views/SamHead.html'));
});

router.get('/SamHead',(req,res)=>{
    res.render(path.resolve('views/SamHead.html'));
});

router.get('/robots.txt',(req,res)=>{
    res.render(path.resolve('views/robots.txt'));
});


router.get('/titans-tower',(req,res)=>{
    res.render(path.resolve('views/titans-tower.html'));
});


module.exports = router;
