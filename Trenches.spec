# -*- mode: python -*-

block_cipher = None


added_files=[
  ('/home/guangzhi/game/Trenches/Trenches_v11/cus_font','cus_font'),
  ('/home/guangzhi/game/Trenches/Trenches_v11/levels','levels'),
  ('/home/guangzhi/game/Trenches/Trenches_v11/objects','objects'),
  ('/home/guangzhi/game/Trenches/Trenches_v11/sounds','sounds'),
  ('/home/guangzhi/game/Trenches/Trenches_v11/ui','ui'),
  ('/home/guangzhi/game/Trenches/Trenches_v11/README.txt','.'),
  ('/home/guangzhi/game/Trenches/Trenches_v11/male-names2.txt','.')
  ]


a = Analysis(['Trenches.py'],
             pathex=['/home/guangzhi/game/Trenches/Trenches_v11'],
             binaries=[],
             datas=added_files,
             hiddenimports=['six','packaging','packaging.version','packaging.specifiers','appdirs','packaging.requirements'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Trenches',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Trenches')
