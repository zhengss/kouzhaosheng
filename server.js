const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 8888;

app.use(cors());
app.use(express.json());
app.use('/uploads', express.static('uploads'));

const dataFile = path.join(__dirname, 'data', 'products.json');
const uploadsDir = path.join(__dirname, 'uploads');

if (!fs.existsSync(dataFile)) {
    const dir = path.dirname(dataFile);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(dataFile, JSON.stringify([], null, 2));
}

if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        const uniqueName = Date.now() + '-' + Math.round(Math.random() * 1E9) + path.extname(file.originalname);
        cb(null, uniqueName);
    }
});

const upload = multer({ storage });

function readProducts() {
    const data = fs.readFileSync(dataFile, 'utf8');
    return JSON.parse(data);
}

function writeProducts(products) {
    fs.writeFileSync(dataFile, JSON.stringify(products, null, 2));
}

app.get('/api/products', (req, res) => {
    try {
        const products = readProducts();
        res.json(products);
    } catch (error) {
        res.status(500).json({ error: '读取产品失败' });
    }
});

app.post('/api/products', upload.single('image'), (req, res) => {
    try {
        const { name, cate, desc } = req.body;
        
        if (!name) {
            return res.status(400).json({ error: '产品名称不能为空' });
        }
        
        if (!req.file) {
            return res.status(400).json({ error: '请上传产品图片' });
        }
        
        const products = readProducts();
        const newProduct = {
            id: Date.now(),
            name,
            cate: cate || '',
            desc: desc || '',
            img: `/uploads/${req.file.filename}`
        };
        
        products.push(newProduct);
        writeProducts(products);
        
        res.json({ success: true, product: newProduct });
    } catch (error) {
        res.status(500).json({ error: '添加产品失败' });
    }
});

app.delete('/api/products/:id', (req, res) => {
    try {
        const id = parseInt(req.params.id);
        let products = readProducts();
        const product = products.find(p => p.id === id);
        
        if (!product) {
            return res.status(404).json({ error: '产品不存在' });
        }
        
        if (product.img && product.img.startsWith('/uploads/')) {
            const imgPath = path.join(__dirname, product.img);
            if (fs.existsSync(imgPath)) {
                fs.unlinkSync(imgPath);
            }
        }
        
        products = products.filter(p => p.id !== id);
        writeProducts(products);
        
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: '删除产品失败' });
    }
});

app.use(express.static('.'));

app.listen(PORT, () => {
    console.log(`服务器运行中: http://localhost:${PORT}`);
});