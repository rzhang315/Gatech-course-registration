# -*- mode: python -*-

block_cipher = None


a = Analysis(['main_app.py'],
             pathex=['C:\\Users\\Ruo\\Desktop\\Enroll\\MSU_ROLL-master\\MSU_ROLL-master\\source_win'],
             binaries=[],
             datas=[],
             hiddenimports=[],
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
          name='GTEnroll',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='sushi.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='GTEnroll')
